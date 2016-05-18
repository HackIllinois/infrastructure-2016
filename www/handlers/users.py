import logging
import json
import re

from www.handlers.base import BaseHandler
from www.services.storage import StorageService, FileValidationException
from www.services.mail import MailService
from www.services.user import UserService
from www import models, utils

REQUEST_CONVERSIONS = {
    'RSVPHandler': {
        'POST': {
            'attending': { 'type': bool }
        }
    },
    'RegistrationHandler': {
        'POST': {
            'age': { 'type': int },
            'graduation_year': { 'type': int },
            'initiatives': { 'type': list, 'delimiter': ',' },
            'team_member_emails': { 'type': list, 'delimiter': ',' }
        }
    }
}

class RSVPHandler(BaseHandler):

    def _handle_common(self, user):
        """
        Returns a tuple containing the following after running
        common error checks and validation
        (errors, parameters)
        """
        parameters = self.request.POST
        parameters = utils.pythonize(dict(parameters))
        parameters = { key: value for (key, value) in parameters.iteritems() if key in models.HackerResponse._properties }

        conversions = REQUEST_CONVERSIONS['RSVPHandler']['POST']
        errors = utils.convert(parameters, conversions)
        if errors:
            self.response.set_status(400)
            return (utils.depythonize(errors), None)

        if not parameters['attending']:
            parameters['transportation'] = None

        return (None, parameters)

    def get(self):
        user = self.user
        registrant = user.descendant() if user else None

        if not user:
            return self.redirect_to('index')
        if not registrant or not isinstance(registrant, models.Hacker) \
            or not registrant.notification_sent or not registrant.status == 'ACCEPTED':
            return self.redirect_to('register')

        data = {}
        data['user'] = user.serialize()
        data['user']['registrant'] = registrant.serialize()

        return self.render('templates/rsvp.html', data=data)

    def post(self):
        user = self.user
        registrant = user.descendant() if user else None

        if not registrant or not isinstance(registrant, models.Hacker) \
            or not registrant.notification_sent or not registrant.status == 'ACCEPTED':
            return self.abort(401)

        errors, parameters = self._handle_common(user)
        if errors:
            return self.write_json(utils.depythonize(errors))

        registrant.response = models.HackerResponse(**parameters)
        registrant.put()

    def put(self):
        user = self.user
        registrant = user.descendant() if user else None

        if not registrant or not isinstance(registrant, models.Hacker) \
            or not registrant.notification_sent or not registrant.status == 'ACCEPTED' \
            or not registrant.response:
            return self.abort(401)

        errors, parameters = self._handle_common(user)
        if errors:
            return self.write_json(utils.depythonize(errors))

        registrant.response.attending = parameters.get('attending')
        registrant.response.transportation = parameters.get('transportation')
        registrant.response.transportation_details = parameters.get('transportation_details')
        registrant.put()

class RegistrationHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user:
            self.redirect(self.uri_for('authenticate'))
            return

        registrant = user.descendant()
        registration = registrant.registration if registrant else None

        data = {}
        data['user'] = user.serialize()
        data['user']['registrant'] = registrant.serialize() if registration else None

        self.render('templates/register.html', data=data)

    def post(self):
        # TODO: make a separate PUT handler for updates
        # instead of using the same POST handler

        user = self.user
        if not user:
            self.redirect(self.uri_for('authenticate'))
            return

        try:
            parameters = self.request.POST
            parameters = utils.pythonize(dict(parameters))

            registrant = user.descendant(create=True)

            # marshal the given parameters
            registrant_allowed = list(type(registrant)._properties)
            registration_allowed = list(models.RegistrationInformation._properties)
            registrant_parameters = {key: value for (key, value) in parameters.iteritems() if key in registrant_allowed}
            registration_parameters = {key: value for (key, value) in parameters.iteritems() if key in registration_allowed}
            resume = registration_parameters.pop('resume', None)

            # ensure that types are correct, returning an error
            # if this is not the case
            conversions = REQUEST_CONVERSIONS['RegistrationHandler']['POST']
            errors = utils.convert(registration_parameters, conversions)
            if errors:
                self.response.set_status(400)
                self.write_json(utils.depythonize(errors))
                return

            # ensure that we didn't get any values passed up
            # for initiative-related questions that the user isn't
            # involved in
            if not 'HARDWARE' in registration_parameters.get('initiatives', []):
                registration_parameters['hardware_desired'] = None
            if not 'OPEN_SOURCE' in registration_parameters.get('initiatives', []):
                registration_parameters['open_source_interests'] = None

            # create/update the registrant's registration information
            if not registrant.registration:
                registrant.update_registrant(registrant_parameters)
                registrant.registration = models.RegistrationInformation(**registration_parameters)
            else:
                registrant.update_registrant(registrant_parameters)
                registrant.update_registration(registration_parameters)

            # create/update the registrant's resume in GCS
            # note that NoneType is tested for explicitly out of necessity
            try:
                if resume is not None:
                    storage_service = StorageService(self.app)

                    old_resume = registrant.registration.resume
                    if old_resume:
                        storage_service.delete(old_resume)

                    try:
                        registrant.registration.resume = storage_service.save_resume(resume)
                    except FileValidationException, e:
                        self.abort(400)

            except Exception, e:
                logging.error("Resume upload failed for %s (ID %d)" % (user.email, user._key.id()))
                logging.exception(e)
                self.abort(500)

            # write the registrant instance to the datastore,
            # even if the resume could not be saved
            registrant.put()

        except Exception, e:
            logging.error("Registration failed for %s (ID %d)" % (user.email, user._key.id()))
            logging.exception(e)
            self.abort(500)

class RegistrationSuccessHandler(BaseHandler):
    def get(self):
        user = self.user
        if not user:
            self.redirect(self.uri_for('authenticate'))
            return

        descendant = user.descendant()
        if not descendant or not descendant.registration:
            self.redirect(self.uri_for('register'))
            return

        data = {}
        data['user'] = user.serialize()
        data['user']['registrant'] = descendant.serialize()
        self.render('templates/register_success.html', data=data)


class SignupHandler(BaseHandler):
  def get(self):
    user = self.user
    if not user:
        self.render('templates/authenticate.html')
        return

    self.redirect(self.uri_for('register'))

  def post(self):
    parameters = self.request.POST
    parameters = utils.pythonize(dict(parameters))

    email = parameters.get("email")
    password = parameters.get("password_raw")
    data = {}
    data["errors"] = {}

    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            data["errors"]["email"] = "This value must be a valid email address"
        elif 'hackillinois.org' in email:
            data["errors"]["email"] = "Your HackIllinois address cannot be used"
    else:
        data["errors"]["email"] = "This value is required"

    if password:
        if len(password) < 8:
            data["errors"]["password"] = "This value must be at least 8 characters"
    else:
        data["errors"]["password"] = "This value is required"

    if data["errors"]:
        self.write_json(json.dumps(data))
        return

    email = email.lower()

    parameters["email"] = email
    #Everyone that uses standard signup is a hacker
    parameters["role"] = "HACKER"

    user_service = UserService(self.app)
    try:
        result = user_service.create_user(parameters, create_descendant=False)
    except Exception, e:
        data["errors"]["email"] = e.message
        self.write_json(json.dumps(data))
        return

    self.auth.set_session(self.auth.store.user_to_dict(result), remember=True)

    data['redirect']= self.uri_for('register')
    self.write_json(json.dumps(data))

class ForgotPasswordHandler(BaseHandler):
    def post(self):
        parameters = self.request.POST
        parameters = dict(parameters)

        email = parameters.get("email")
        data = {}
        data["errors"] = {}
        data["messages"] = {}

        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                data["errors"]["email"] = "This value must be a valid email address"
        else:
            data["errors"]["email"] = "This value is required"

        if data["errors"]:
            self.response.set_status(400)
            self.write_json(json.dumps(data))
            return

        email = email.lower()
        user = models.User.query().filter(models.User.email == email).fetch(1)

        if not user:
            data["errors"]["email"] = "No user exists with this email."
            self.write_json(json.dumps(data))
            return

        user = user[0]
        token = self.auth.store.user_model.create_reset_token(user.get_id())
        reset_url = self.request.host_url + "/reset?user=" + str(user.get_id())
        reset_url = reset_url + "&token=" + token

        body = "Hi,\n\nYou recently requested a password reset. To reset your password, use the link below:\n%s"
        body = body % reset_url
        subject = "Password Reset"

        mail_service = MailService(self.app)
        mail_service.send(email, subject, body)

        data["messages"]["success"] = "An email has been sent with instructions on how to reset your password."
        self.write_json(json.dumps(data))
