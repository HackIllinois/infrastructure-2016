import json
import datetime
import logging
import csv

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import deferred
from google.appengine.ext import ndb

from www.handlers.base import BaseHandler
from www.services.user import UserService, UserException
from www import errors, models, response_utils, utils, deferreds

REQUEST_CONVERSIONS = {
    'UserManagementHandler': {
        'POST': {
            'organization': { 'type': int },
            'walk_in': { 'type': bool },
            'hardware': { 'type': bool },
            'is_new_organization': { 'type': bool }
        }
    }
}

MIN_WAVE = 1
MAX_WAVE = 12
UIUC_SCHOOL_ = 'university of illinois - urbana-champaign'

class BaseDataTableHandler(BaseHandler):
    COLUMNS = { }
    ORDERABLE_COLUMNS = [ ]

    def _pre_post(self):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.abort(401)
            return
        return user

    def _post_parameters(self):
        parameters = {}
        parameters['draw'] = self.request.get_range('draw')
        parameters['page'] = self.request.get_range('page')
        parameters['limit'] = self.request.get_range('length', max_value=100)
        parameters['offset'] = self.request.get_range('start')
        parameters['cursor'] = self.request.get('cursor')
        return parameters

    def _post_aggregate(self):
        search = None
        search_column = None
        orders = []
        for index in range(0, len(self.__class__.COLUMNS)):
            search_by = self.request.get('columns[%d][search][value]' % index)
            order_by = self.request.get('order[%d][column]' % index)
            order_dir = self.request.get('order[%d][dir]' % index)

            if search_by:
                search = search_by
                search_column = str(index)
            if order_by in self.__class__.ORDERABLE_COLUMNS:
                order_by = -self.__class__.COLUMNS.get(order_by)
                order_by = order_by.reversed() if order_dir == 'asc' else order_by
                orders.append(order_by)
        return search, search_column, orders

    def _compute_records_total(self, parameters, more):
        # we trick the front-end by falsely calculating the
        # total records. In this way, we don't have to do
        # a much more costly count() query
        records_total = (parameters['page'] + 1) * parameters['limit']
        if more:
            records_total += 1
        return records_total

class DashboardHandler(BaseHandler):

    def get(self):
        user = self.user
        if not user or not user.has_role('ADMINISTRATOR'):
            return self.redirect_to('admin_home')

        # these stats are generated daily
        # however, they may be unavailable while they are being generated
        query = models.DashboardStats.query()
        query = query.filter(models.DashboardStats.incomplete == False)
        stats = query.get()

        data = {}
        data['user'] = user.serialize()
        data['stats'] = stats.serialize() if stats else None
        self.render('templates/admin_dashboard.html', data=data)


class NotificationWaveHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('authenticate'))
            return

        data = {}
        sent_waves = [notification.wave for notification in models.NotificationWave.query().fetch()]
        waves = []
        for x in xrange(MIN_WAVE, MAX_WAVE + 1):
            wave = {'wave': x, 'disabled': x in sent_waves}
            waves.append(wave)

        data['waves'] = waves
        data['user'] = user.serialize()
        self.render("templates/admin_notify.html", data=data)

class SendNotificationWaveHandler(BaseHandler):
    def post(self, wave):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            return
        try:
            wave = int(wave)
        except ValueError:
            wave = -1

        wave_query = models.NotificationWave.query()
        wave_query = wave_query.filter(models.NotificationWave.wave == wave)
        existing_wave = wave_query.fetch(1)
        if existing_wave or wave < MIN_WAVE or wave > MAX_WAVE:
            return self.abort(400)

        app = self.app.config
        root_url = self.request.host_url

        #For waitlist-closed notification
        if wave == 11:
            deferred.defer(deferreds.WaitlistClosedNotificationDeferred, app_config=app, root_url=root_url, wave=wave)
            return

        #For all hackers that have rsvp'd
        if wave == 12:
            deferred.defer(deferreds.RSVPedHackerNotificationDeferred, app_config=app, root_url=root_url, wave=wave)
            return

        #For sending out lob codes
        if wave == 13:
            deferred.defer(deferreds.ApiNotificationDeferred, app_config=app, wave=wave)
            return

        deferred.defer(deferreds.DecisionNotificationDeferred, app_config=app, root_url=root_url, wave=wave)

class HomeHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('authenticate'))
            return

        data = {}
        data['user'] = user.serialize()
        self.render("templates/admin_home.html", data=data)

class NetworkCredentialsUploadHandler(BaseHandler):
    @ndb.transactional(xg=True)
    def _handle_creation(self, credentials):
        ndb.put_multi(credentials)

    def post(self):
        user = self.user
        if not user or not user.has_role('ADMINISTRATOR'):
            return self.abort(401)

        credentials = self.request.get('credentials')
        credentials = str(credentials)
        prepared = 0

        try:
            credentials = credentials.splitlines()
            data = []

            for credential in credentials:
                credential = "".join(credential.strip().split())
                login, password = credential.split(',')

                data.append(models.NetworkCredentials(login=login, password=password))
                prepared += 1

            if prepared > 0:
                # create the remaining entities
                self._handle_creation(data)
        except ValueError, e:
            # since this is a particularly sensitive manual operation,
            # we want to be as descriptive as possible as to what went wrong
            issue = credentials[prepared]

            error_description = "Value '%s' is invalid" % issue
            error_source = str(prepared)
            response = response_utils.make_error(errors.InvalidParameterError(error_description, error_source))

            self.response.set_status(response['meta']['status'])
            return self.write_json(json.dumps(response))

    def get(self):
        user = self.user
        if not user or not user.has_role('ADMINISTRATOR'):
            return self.redirect_to('admin_home')

        data = {}
        data['user'] = user.serialize()
        self.render("templates/admin_netcred_upload.html", data=data)

class UserViewHandler(BaseHandler):
    def _retrieve_subject(self, user_id):
        try:
            user_id = long(user_id)
        except ValueError:
            self.abort(404)

        subject = models.User.get_by_id(user_id) if user_id < 2L ** 63 else None
        descendant = subject.descendant() if subject else None

        return subject, descendant

    def _make_data(self, user, subject=None, descendant=None):
        data = {}
        data['user'] = user.serialize()
        data['subject'] = subject.serialize() if subject else None
        data['subject']['id'] = subject._key.id() if subject else None
        data['subject']['descendant'] = descendant.serialize() if subject and descendant else None

        return data

    def get(self, user_id):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            return self.abort(401)

        subject, descendant = self._retrieve_subject(user_id)
        if not subject: return self.abort(404)

        data = self._make_data(user, subject, descendant)
        self.render("templates/admin_users_view.html", data=data)

    def put(self, user_id):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            return self.abort(401)

        subject, descendant = self._retrieve_subject(user_id)
        if not subject: return self.abort(404)

        # there are only a few attributes that we allow
        # to be updated, and they may only be updated
        # one at a time
        if self.request.get('shirt_collected'):
            descendant.shirt_collected = True
            return descendant.put()
        if self.request.get('swag_collected'):
            descendant.swag_collected = True
            return descendant.put()
        if self.request.get('is_volunteering'):
            descendant.is_volunteering = True
            return descendant.put()

        meal = self.request.get('meal')
        if not meal in models.MealEntry.MEAL_OPTIONS:
            return self.abort(401)

        meal = models.MealEntry(identity=meal)
        descendant.meals.append(meal)
        descendant.put()

class UserManagementHandler(BaseHandler):
    def get(self, mode):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('authenticate'))
            return

        organizations = [{"name": organization.name , "id": organization.key.id()} for organization in models.Organization.query().fetch()]
        data = { 'mode': mode }
        data['organizations'] = organizations
        data['user'] = user.serialize()
        self.render("templates/admin_users.html", data=data)

    def post(self, mode):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.abort(401)
            return

        parameters = self.request.POST
        parameters = utils.pythonize(dict(parameters))

        email = parameters.get('email')
        if email:
            parameters['email'] = email.lower()

        # ensure that types are correct, returning an error
        # if this is not the case
        conversions = REQUEST_CONVERSIONS['UserManagementHandler']['POST']
        errors = utils.convert(parameters, conversions)
        if errors:
            self.response.set_status(400)
            self.write_json(json.dumps(utils.depythonize(errors)))
            return

        organization_id = parameters.get('organization')
        if organization_id:
            organization = models.Organization.get_by_id(organization_id)
            # update parameters to hold Organization as StructuredProperty instead of id
            parameters['organization'] = organization

        is_new_organization =  parameters.get('is_new_organization')
        if is_new_organization:
            organization_name = parameters.get('organization_name')
            organization_tier = parameters.get('organization_tier')
            hardware = parameters.get('hardware')
            organization = models.Organization.query(models.Organization.name_ == organization_name.lower()).get()
            if not organization:
                organization = models.Organization(name = organization_name, sponsorship = organization_tier)
                organization.put()
                if hardware:
                    #create new organization permission
                    models.Permission.add_organization_permission(organization.key.id(), 'hackillinois.hardware.checkout')
            # update parameters to hold Organization as StructuredProperty instead of id
            parameters['organization'] = organization


        role = str(parameters.get('role'))
        if user.has_role('STAFF') and role in ['ADMINISTRATOR', 'STAFF']:
            return self.abort(401)
        if role == 'SPONSOR' and organization:
            if organization.sponsorship and organization.sponsorship in models.SPONSORSHIP_OPTIONS:
                role = role + "T" + str(models.SPONSORSHIP_OPTIONS.index(organization.sponsorship))
                parameters['role'] = role
        if role == 'HACKER':
            parameters['notification_wave'] = 0
            parameters['notification_sent'] = datetime.datetime.now()
            parameters['reviewer'] = user.email

        user_service = UserService(self.app)
        try:
            user = user_service.create_user(parameters)

            reset_token = self.auth.store.user_model.create_reset_token(user.get_id())
            host_url = self.request.host_url
            user_service.send_new_user_email(host_url, reset_token, user)
        except UserException, e:
            errors = { "errors": [{ "name": e.name, "message": e.message }] }
            self.response.set_status(400)
            self.write_json(json.dumps(utils.depythonize(errors)))
            return

class SearchHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user:
            self.abort(400)
            return
        if not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.abort(401)
            return

        query = self.request.get('query', None)
        result = None
        if query:
            result = models.User.query().filter(query.lower() == models.User.email).fetch(1)
        if not result:
            self.write_json(json.dumps({ "error": { "message": "Not found" } }))
            return

        self.write_json(json.dumps({ "data": { "id": result[0].key.id() } }));

class CheckinHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user:
            self.redirect_to('authenticate')
            return
        if not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect_to('index')
            return

        data = {}
        data['user'] = user.serialize()
        self.render('templates/admin_checkin.html', data=data)

class CheckinDataHandler(BaseHandler):

    @ndb.transactional(xg=True)
    def _persist_checkin(self, subject, descendant, credentials, credentials_needed):
        if credentials_needed:
            credentials.assignment = subject._key
            credentials.assigned = True

            descendant.network_credentials = models.AbbreviatedNetworkCredentials()
            descendant.network_credentials.login = credentials.login
            descendant.network_credentials.password = credentials.password

            credentials.put()

        descendant.checked_in = datetime.datetime.now()
        descendant.put()

    def post(self, user_id):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            return self.abort(401)

        try:
            user_id = long(user_id)
        except ValueError:
            self.abort(404)

        subject = models.User.get_by_id(user_id)
        descendant = subject.descendant() if subject else self.abort(404)

        if descendant.checked_in:
            return self.abort(400)

        network_credentials = None
        credentials_unecessary = subject.has_roles(['ADMINISTRATOR', 'STAFF', 'VOLUNTEER'])
        credentials_unecessary = credentials_unecessary or (descendant.registration.school_ == UIUC_SCHOOL_ if (subject.role == 'HACKER' and descendant.registration) else False)
        credentials_needed = not credentials_unecessary # note that we do it this way to make things slightly more readable

        if credentials_needed:
            credentials_query = models.NetworkCredentials.query()
            credentials_query = credentials_query.filter(models.NetworkCredentials.assigned == False)
            network_credentials =credentials_query.get()

        if not network_credentials and credentials_needed:
            logging.error("No network credentials are available for assignment")
            return self.abort(500)

        self._persist_checkin(subject, descendant, network_credentials, credentials_needed)

        result = { 'credentials': network_credentials.serialize() if network_credentials else None }
        response = response_utils.make_response(result)
        self.write_json(json.dumps(response))

    def get(self, user_id):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            return self.redirect_to('authenticate')

        try:
            user_id = long(user_id)
        except ValueError:
            self.abort(404)

        subject = models.User.get_by_id(user_id)
        descendant = subject.descendant() if subject else self.abort(404)

        data = {}
        data['user'] = user.serialize()
        data['subject'] = subject.serialize()
        data['subject']['id'] = subject._key.id()
        data['subject']['descendant'] = descendant.serialize()

        self.render('templates/admin_checkin_details.html', data=data)

class CheckinDataTableHandler(BaseDataTableHandler):
    COLUMNS = {
        '0': models.Person.first_name_,
        '1': models.Person.last_name_,
        '2': models.RegisteredPerson.registration.school_,
        '3': models.RegisteredPerson.registration.graduation_year,
        '4': models.OrganizationalPerson.organization.name_,
        '5': models.Person.checked_in
    }

    ORDERABLE_COLUMNS = ['1', '3']

    def _post_search(self, search, search_column):
        search = str(search).strip().lower() if search else None
        valid = True

        if not search:
            return search, valid

        if search_column == "3":
            try:
                search = int(search)
            except ValueError:
                search_valid = False

        return search, valid

    def _post_model(self):
        model = self.request.get('model')
        model = models.User.descendant_model(model)
        return model if model else models.Hacker

    def post(self):
        user = self._pre_post()
        if not user:
            return

        # pull together all of the necessary parameters
        parameters = self._post_parameters()
        search, search_column, orders = self._post_aggregate()
        search, search_valid = self._post_search(search, search_column)
        model = self._post_model()

        # build the query
        query = model.query()
        for order in orders:
            query = query.order(order)
        if search_valid and search:
            search_column = CheckinDataTableHandler.COLUMNS[search_column]
            query = query.filter(search_column == search)

        offset = parameters['offset']
        cursor = None
        data, more = [], False

        if search_valid:
            cursor = Cursor(urlsafe=parameters['cursor'])
            data, cursor, more = query.fetch_page(parameters['limit'], offset=0, start_cursor=cursor)

        serialized_data = []
        for result in data:
            has_registration = hasattr(result, 'registration') and result.registration
            has_organization = hasattr(result, 'organization') and result.organization

            value = {}
            value['id'] = result.key.parent().id()
            value['firstName'] = result.first_name
            value['lastName'] = result.last_name
            value['school'] = result.registration.school if has_registration else 'N/A'
            value['graduation'] = result.registration.graduation_year if has_registration else 'N/A'
            value['organization'] = result.organization.name if has_organization else 'N/A'
            value['checkIn'] = utils.to_epoch_seconds(result.checked_in) if result.checked_in else None
            serialized_data.append(value)

        records_total = self._compute_records_total(parameters, more)

        self.write_json(json.dumps({
            "draw": parameters['draw'],
            "data": serialized_data,
            "recordsTotal": records_total,
            "recordsFiltered": records_total,
            "cursor": cursor.urlsafe() if cursor else None
        }))

class ReviewHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user:
            self.redirect(self.uri_for('authenticate'))
            return
        if not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('index'))
            return

        data = {}
        data['user'] = user.serialize()
        self.render('templates/admin_review.html', data=data)

class ReviewDetailsHandler(BaseHandler):
    def get(self, user_id):
        user = self.user
        if not user:
            self.redirect(self.uri_for('authenticate'))
            return
        if not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('index'))
            return

        try:
            user_id = long(user_id)
        except ValueError:
            self.abort(404)

        subject = models.User.get_by_id(user_id)
        registrant = subject.descendant() if subject else self.abort(404)

        data = {}
        data['user'] = user.serialize()
        data['subject'] = subject.serialize()
        data['subject']['registrant'] = registrant.serialize() if registrant else {}
        data['waves_sent'] = [notification.wave for notification in models.NotificationWave.query().fetch()]

        self.render('templates/admin_review_details.html', data=data)

    def put(self, user_id):
        user = self.user
        if not user:
            self.abort(400)
        if not user.has_roles(['ADMINISTRATOR']):
            self.abort(401)

        try:
            user_id = long(user_id)
        except ValueError:
            self.abort(404)

        subject = models.User.get_by_id(user_id)

        registrant = subject.descendant() if subject else self.abort(404)
        registrant.status = self.request.get('status', 'PENDING')
        registrant.initiative = self.request.get('initiative', None)
        registrant.notification_wave = self.request.get_range('wave')
        registrant.reviewer = user.email

        user_service = UserService(self.app)
        subject_permissions = subject.permissions
        if registrant.status != 'ACCEPTED':
            subject.permissions = user_service.remove_helpq_common_permission(subject_permissions)
        else:
            subject.permissions = user_service.add_helpq_common_permission(subject_permissions, 'HACKER')

        registrant.put()
        subject.put()

class ReviewDataTableHandler(BaseDataTableHandler):

    COLUMNS = {
        '0': models.Hacker.first_name_,
        '1': models.Hacker.last_name_,
        '2': models.Hacker.registration.gender,
        '3': models.Hacker.registration.school_,
        '4': models.Hacker.registration.graduation_year,
        '5': models.Hacker.registration.major_,
        '6': models.Hacker.registration.initiatives,
        '7': models.Hacker.registration.created,
        '8': models.Hacker.status,
        '9': models.Hacker.notification_wave
    }

    ORDERABLE_COLUMNS = ['1', '4', '7', '9']

    def _post_search(self, search, search_column):
        search = str(search).strip().lower() if search else None
        valid = True

        if not search:
            return search, valid

        if search_column in ["4", "9"]:
            try:
                search = int(search)
            except ValueError:
                search_valid = False
        elif search_column == "2":
            search = search.upper()
            search = search.replace(' ', '_')
            if search not in models.GENDER_OPTIONS:
                search_valid = False
        elif search_column == "6":
            search = search.upper().strip()
            search = search.replace(' ', '_')
            if search not in models.INITIATIVE_OPTIONS:
                search_valid = False
        elif search_column == "8":
            search = search.upper().strip()
            if search not in models.STATUS_OPTIONS:
                search_valid = False

        return search, valid

    def post(self):

        user = self._pre_post()
        if not user:
            return

        # pull together all of the necessary parameters
        parameters = self._post_parameters()
        search, search_column, orders = self._post_aggregate()
        search, search_valid = self._post_search(search, search_column)

        # build the query
        query = models.Hacker.query()
        for order in orders:
            query = query.order(order)
        if search_valid and search:
            search_column = ReviewDataTableHandler.COLUMNS[search_column]
            query = query.filter(search_column == search)

        offset = parameters['offset']
        cursor = None
        data, more = [], False

        if search_valid:
            cursor = Cursor(urlsafe=parameters['cursor'])
            data, cursor, more = query.fetch_page(parameters['limit'], offset=0, start_cursor=cursor)

        # the data that we send back is slightly different
        # than what the serializer would yield; we can't include
        # extra fields either
        serialized_data = [{
            "firstName": registrant.first_name,
            "lastName": registrant.last_name,
            "gender": registrant.registration.gender,
            "school": registrant.registration.school,
            "graduation": registrant.registration.graduation_year,
            "major": registrant.registration.major,
            "initiatives": registrant.registration.initiatives,
            "registered": registrant.registration.created,
            "status": registrant.status,
            "wave": registrant.notification_wave,
            "id": registrant.key.parent().id()
        } for registrant in data if registrant.registration]

        records_total = self._compute_records_total(parameters, more)

        self.write_json(json.dumps({
            "draw": parameters['draw'],
            "data": serialized_data,
            "recordsTotal": records_total,
            "recordsFiltered": records_total,
            "cursor": cursor.urlsafe() if cursor else None
        }))

class HardwareSecretHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user or not user.has_roles(['ADMINISTRATOR', 'STAFF']):
            self.redirect(self.uri_for('authenticate'))
            return

        data = {'secret': self.app.config['hardware_api']['secret_key']}
        self.write_json(json.dumps(data))
