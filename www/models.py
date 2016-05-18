from google.appengine.ext import ndb

from webapp2_extras import security
import webapp2_extras.appengine.auth.models

import time
import www.utils

from datetime import datetime, timedelta

BOTTOM_SPONSOR_TIER = 1
TOP_SPONSOR_TIER = 5

YES_NO_MAYBE_OPTIONS = ['YES', 'NO', 'MAYBE']
SPONSORSHIP_OPTIONS = ['NONE', 'SQUIRREL', 'OWL', 'MOOSE', 'BEAR', 'WOLF']
SHIRT_SIZE_OPTIONS = ['XS', 'S', 'M', 'L', 'XL']
GENDER_OPTIONS = ['NONE', 'MALE', 'FEMALE', 'NON_BINARY', 'OTHER']
DIET_OPTIONS = ['NONE', 'VEGETARIAN', 'VEGAN', 'GLUTEN_FREE']
HACKATHON_ATTENDANCE_OPTIONS = ['0', '1-5', '5+']
PROFESSIONAL_OPTIONS = ['NONE', 'FULL_TIME', 'INTERNSHIP', 'BOTH']
INITIATIVE_OPTIONS = ['SOFTWARE', 'HARDWARE', 'OPEN_SOURCE']
STATUS_OPTIONS = ['ACCEPTED', 'REJECTED', 'WAITLISTED', 'PENDING']
ROLE_OPTIONS = ["ADMINISTRATOR", "STAFF", "MENTOR", "SPONSORT1", "SPONSORT2",
    "SPONSORT3", "SPONSORT4", "SPONSORT5", "VOLUNTEER", "HACKER"]

class Model(ndb.Model):

    @classmethod
    def delete(cls, key):
        if not isinstance(key, ndb.Key):
            key = ndb.Key(cls, key)

        if key:
            key.delete()

    def serialize(self):
        return self.to_dict()

class NotificationWave(Model):
    """
    Indicates that a certain wave has been sent out.
    """
    wave = ndb.IntegerProperty(required=True, indexed=True)
    created = ndb.DateTimeProperty(indexed=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(indexed=True, auto_now=True)

class Configuration(Model):
    """
    Stores sensitive configuration information for application
    """

    @classmethod
    def _clear(cls):
        ndb.delete_multi(cls.query().fetch(keys_only=True))

    admin_password = ndb.StringProperty(indexed=False)
    session_secret = ndb.StringProperty(indexed=False)

class RawCredentials(Model):

    login = ndb.StringProperty()
    password = ndb.StringProperty(indexed=False)

class AbbreviatedNetworkCredentials(RawCredentials):
    pass

class NetworkCredentials(RawCredentials):

    assigned = ndb.BooleanProperty(default=False)
    assignment = ndb.KeyProperty(kind='User')

class DashboardInitiativeStats(Model):

    accepted = ndb.IntegerProperty(indexed=False)
    rsvp = ndb.IntegerProperty(indexed=False)

class DashboardApplicantStats(Model):

    total = ndb.IntegerProperty(indexed=False)

    software = ndb.StructuredProperty(DashboardInitiativeStats)
    hardware = ndb.StructuredProperty(DashboardInitiativeStats)
    open_source = ndb.StructuredProperty(DashboardInitiativeStats)

    waitlisted = ndb.IntegerProperty(indexed=False)
    rejected = ndb.IntegerProperty(indexed=False)


class DashboardBusStats(Model):
    not_needed = ndb.IntegerProperty(indexed=False)
    driving = ndb.IntegerProperty(indexed=False)
    bus_uic_iit_uchicago = ndb.IntegerProperty(indexed=False)
    bus_northwestern_depaul = ndb.IntegerProperty(indexed=False)
    bus_ku_mizzou = ndb.IntegerProperty(indexed=False)
    bus_purdue = ndb.IntegerProperty(indexed=False)
    bus_rose_hulman = ndb.IntegerProperty(indexed=False)
    bus_northwestern = ndb.IntegerProperty(indexed=False)
    bus_uic_depaul = ndb.IntegerProperty(indexed=False)
    bus_iit_uchicago = ndb.IntegerProperty(indexed=False)
    bus_florida_georgia_tech = ndb.IntegerProperty(indexed=False)
    bus_wisconsin_madison = ndb.IntegerProperty(indexed=False)

class DashboardStats(Model):
    """
    Stores commonly-needed statistics
    """

    applicant = ndb.StructuredProperty(DashboardApplicantStats)
    bus = ndb.StructuredProperty(DashboardBusStats)
    incomplete = ndb.BooleanProperty(default=True)

class MealEntry(Model):
    """
    Stores data about a meal
    """
    MEAL_OPTIONS = ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'MINI_MEAL']

    created = ndb.DateTimeProperty(auto_now_add=True)
    identity = ndb.StringProperty(choices=MEAL_OPTIONS)

class Person(Model):
    """
    Provides the properties required to make a model
    that has the characteristics of a person
    """

    first_name = ndb.StringProperty(required=True, indexed=False)
    first_name_ = ndb.ComputedProperty(lambda self: self.first_name.lower(), indexed=True)
    last_name = ndb.StringProperty(required=True, indexed=False)
    last_name_ = ndb.ComputedProperty(lambda self: self.last_name.lower(), indexed=True)

    checked_in = ndb.DateTimeProperty(indexed=True)
    meals = ndb.StructuredProperty(MealEntry, repeated=True)
    network_credentials = ndb.StructuredProperty(AbbreviatedNetworkCredentials)

    phone_number = ndb.StringProperty(indexed=True)
    shirt_size = ndb.StringProperty(indexed=True, choices=SHIRT_SIZE_OPTIONS)
    shirt_collected = ndb.BooleanProperty(indexed=True, default=False)
    swag_collected = ndb.BooleanProperty(indexed=True, default=False)

class VolunteeringPerson(Person):
    """
    Provides the properties required to make a model
    that has the characteristics of a person who may
    be volunteering at the event
    """
    is_volunteering = ndb.BooleanProperty(default=False)

class RegistrationInformation(Model):
    """
    Information collected via the primary registration
    method.
    """

    created = ndb.DateTimeProperty(indexed=True, auto_now_add=True)

    age = ndb.IntegerProperty(required=True, indexed=True)
    gender = ndb.StringProperty(required=True, indexed=True, choices=GENDER_OPTIONS)
    school = ndb.StringProperty(required=True, indexed=False)
    school_ = ndb.ComputedProperty(lambda self: self.school.lower(), indexed=True)
    graduation_year = ndb.IntegerProperty(required=True, indexed=True)
    major = ndb.StringProperty(required=True, indexed=False)
    major_ = ndb.ComputedProperty(lambda self: self.major.lower(), indexed=True)

    diet = ndb.StringProperty(required=True, choices=DIET_OPTIONS, indexed=True)
    dietary_restrictions = ndb.StringProperty(indexed=True)

    resume = ndb.BlobKeyProperty(required=True)
    resume_filename = ndb.StringProperty(required=True, indexed=False)
    professional_interest = ndb.StringProperty(required=True, choices=PROFESSIONAL_OPTIONS, indexed=True)
    linkedin_url = ndb.StringProperty(indexed=False)
    github_url = ndb.StringProperty(indexed=False)
    site_url = ndb.StringProperty(indexed=False)

    hackathon_attendance = ndb.StringProperty(required=True, choices=HACKATHON_ATTENDANCE_OPTIONS, indexed=True)
    initiatives = ndb.StringProperty(repeated=True, choices=INITIATIVE_OPTIONS)

    team_member_emails = ndb.StringProperty(repeated=True)
    hardware_desired = ndb.StringProperty(indexed=True)
    open_source_interests = ndb.StringProperty(indexed=True)
    extra_information = ndb.StringProperty(indexed=False)

class RegisteredPerson(Person):
    """
    Provides the properties and functionality required to make a model
    that has that characteristics of a person that will
    eventually be registered for the event
    """

    registration = ndb.StructuredProperty(RegistrationInformation)

    def update_registrant(self, values):
        for key, value in values.iteritems():
            if key in ['first_name', 'last_name', 'shirt_size', 'phone_number']:
                setattr(self, key, value)
                continue

    def update_registration(self, values):
        for key, value in values.iteritems():
            if key not in ['Key', 'Write Ops', 'ID', 'Key Name', 'resume']:
                if hasattr(self.registration, key):
                    setattr(self.registration, key, value)

    def update(self, values):
        self.update_registrant(values)
        self.update_registration(values)

class Organization(Model):
    """
    Stores the identity of an organization that will be present at the
    hackathon. The organization may or may not be sponsoring the event
    """

    name = ndb.StringProperty(required=True, indexed=False)
    name_ = ndb.ComputedProperty(lambda self: self.name.lower(), indexed=True)
    sponsorship = ndb.StringProperty(choices=SPONSORSHIP_OPTIONS, default='NONE')

class OrganizationalPerson(Person):
    """
    Provides the properties required to make a model
    that has the characteristics of a person that is part
    of an organization
    """

    organization = ndb.StructuredProperty(Organization, required=True)

class Volunteer(VolunteeringPerson):
    """
    A person that will be working at the event but will not
    necessarily have any definitive responsibilities.
    """
    pass

class SponsorT1(OrganizationalPerson):
    """
    A representative for a sponsor of the first tier
    """
    pass

class SponsorT2(OrganizationalPerson):
    """
    A representative for a sponsor of the second tier
    """
    pass

class SponsorT3(OrganizationalPerson):
    """
    A representative for a sponsor of the third tier
    """
    pass

class SponsorT4(OrganizationalPerson):
    """
    A representative for a sponsor of the fourth tier
    """
    pass

class SponsorT5(OrganizationalPerson):
    """
    A representative for a sponsor of the fifth tier
    """
    pass

class Mentor(OrganizationalPerson):
    """
    An person that is dedicated to mentoring
    students at the event
    """
    pass

class Staff(RegisteredPerson):
    """
    A person that will be working at the event
    and has several definitive responsibilities
    """
    pass

class Administrator(RegisteredPerson):
    """
    A person that will be managing the event
    and has access to all resources
    """
    pass

class HackerResponse(Model):

    TRANSPORTATION_OPTIONS = ['NOT_NEEDED', 'DRIVING', 'BUS_UIC_IIT_UCHICAGO',
        'BUS_NORTHWESTERN_DEPAUL', 'BUS_KU_MIZZOU', 'BUS_PURDUE', 'BUS_ROSE_HULMAN',
        'BUS_NORTHWESTERN', 'BUS_UIC_DEPAUL', 'BUS_IIT_UCHICAGO', 'BUS_FLORIDA_GEORGIA_TECH', 'BUS_WISCONSIN_MADISON']

    created = ndb.DateTimeProperty(auto_now_add=True)
    attending = ndb.BooleanProperty(required=True, indexed=True)
    transportation = ndb.StringProperty(indexed=True, choices=TRANSPORTATION_OPTIONS)
    transportation_details = ndb.StringProperty(indexed=False)

class Hacker(RegisteredPerson, VolunteeringPerson):
    """
    A person that will be participating in the event
    as a walk-in or pre-registered hacker

    All Hackers have a status, where PENDING is the
    default. Whenever this changes, the reviewer's email
    is set to 'reviewer'. And the notification wave is updated
    accordingly.

    Later, the Hacker's response is recorded, and the check-in
    date is stored when the Hacker is actually checked in at the
    hackathon. If the Hacker is a walk-in, this is recorded as well
    """

    walk_in = ndb.BooleanProperty(required=True, default=False, indexed=True)

    status = ndb.StringProperty(required=True, default='PENDING', choices=STATUS_OPTIONS, indexed=True)
    reviewer = ndb.StringProperty()
    initiative = ndb.StringProperty(choices=INITIATIVE_OPTIONS, indexed=True)
    notification_wave = ndb.IntegerProperty()
    notification_wave_sent = ndb.IntegerProperty()
    notification_sent = ndb.DateTimeProperty()

    response = ndb.StructuredProperty(HackerResponse)

class Permission(Model):
    """
    A scoped permission that is used to allow
    users to perform certain actions or access
    certain resources

    The GLOBAL scope is reserved for permissions
    that can apply to any user, regardless of standing

    The HELPQ scope is limited to

    The ROLE scope is reserved for permissions
    that are given to users with a specific role

    The ORGANIZATION scope is reserved for
    permissions that are given to users who
    are part of a specific organization

    Targets for these permissions are optional,
    but should be present for all permissions
    except for those in the GLOBAL/UNIQUE scope. An
    example target for the ROLE scope would be
    'ADMINISTRATOR'

    Permissions for HackIllinois' content should be prefixed
    with 'hackillinois'. For example, a permission might be
    'hackillinois.home.view' for viewing the homepage
    """

    SCOPE_OPTIONS = ['GLOBAL', 'ROLE', 'ORGANIZATION', 'UNIQUE']

    scope = ndb.StringProperty(required=True, choices=SCOPE_OPTIONS)
    target = ndb.StringProperty()
    permission = ndb.StringProperty(required=True)

    @classmethod
    def get(cls, scope, permission, target=None):
        if scope not in cls.SCOPE_OPTIONS:
            raise ValueError('Scope [%s] is not valid' % scope)

        query = cls.query().filter(cls.scope == scope)
        query = query.filter(cls.permission == permission)
        query = query.filter(cls.target == target) if target else query

        result = query.fetch(1)
        return result[0] if result else None

    @classmethod
    def __add(cls, scope, permission, target=None):
        existing = cls.get(scope, permission, target)
        if existing:
            return existing

        permission = cls(scope=scope, permission=permission, target=target)
        permission.put()
        return permission

    @classmethod
    def add_global_permission(cls, permission):
        return cls.__add(scope='GLOBAL', permission=permission)

    @classmethod
    def add_role_permission(cls, role, permission):
        if not role in ROLE_OPTIONS:
            raise ValueError("The given role [%s] is not a valid role" % role)

        return cls.__add(scope='ROLE', permission=permission, target=role)

    @classmethod
    def add_organization_permission(cls, organization_id, permission):
        if not isinstance(organization_id, long) or isinstance(organization_id, int):
            raise ValueError("The given organization ID is not a valid ID")

        return cls.__add(scope='ORGANIZATION', permission=permission, target=str(organization_id))

    @classmethod
    def add_unique_permission(cls, permission):
        return cls.__add(scope='UNIQUE', permission=permission)

class UserToken(Model, webapp2_extras.appengine.auth.models.UserToken):
    """
    Stores validation tokens for Users
    """
    user = ndb.StringProperty(required=True, indexed=True)
    expiration = ndb.DateTimeProperty()

    @classmethod
    def create(cls, user, subject, token=None, expiration=None, delete_past_tokens=False):
        """Creates a new token for the given user.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param token:
            Optionally an existing token may be provided.
            If None, a random token will be generated.
        :returns:
            The newly created :class:`UserToken`.
        """

        user = str(user)
        token = token or security.generate_random_string(entropy=128)
        key = cls.get_key(user, subject, token)

        if delete_past_tokens:
            ndb.delete_multi(cls.query(cls.user == user, cls.subject == subject).iter(keys_only=True))

        entity = cls(key=key, user=user, subject=subject, token=token, expiration=expiration)
        entity.put()
        return entity

    @classmethod
    def get(cls, user=None, subject=None, token=None):
        """Fetches a user token.

        :param user:
            User unique ID.
        :param subject:
            The subject of the key. Examples:

            - 'auth'
            - 'signup'
        :param token:
            The existing token needing verified.
        :returns:
            A :class:`UserToken` or None if the token does not exist.
        """
        user_token = None
        if user and subject and token:
            user_token = cls.get_key(user, subject, token).get()
        else:
            user_token = cls.query(cls.subject == subject, cls.token == token).get()

        if user_token and user_token.expiration:
            if datetime.today() > user_token.expiration:
                cls.get_key(user, subject, token).delete()
                return None
        return user_token

class User(Model, webapp2_extras.appengine.auth.models.User):

    email = ndb.ComputedProperty(lambda self: self.auth_ids[0], indexed=True)

    role = ndb.StringProperty(required=True, choices=ROLE_OPTIONS, indexed=True)
    permissions = ndb.StructuredProperty(Permission, repeated=True)

    token_model = UserToken

    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        """Returns a user object based on a user ID, token, and token subject.
        Overriden from webapp2_extras.appengine.auth.models.User

        The 'subject' allows one to have multiple types of tokens, specifically, tokens
        tokens for authentication and tokens for password reset.

        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :param subject
            The subject of the token
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp

        return None, None

    @classmethod
    def create_auth_token(cls, user_id):
        """Creates a new authorization token for a given user ID.
            Overriden from webapp2_extras.appengine.auth.models.User

            An expiration is set for all auth tokens created

        :param user_id:
            User unique ID.
        :returns:
            A string with the authorization token.
        """

        # TODO take expiration hours out of here and put it into
        # app configuration
        expiration_hours = 7 * 24 # one week
        expiration = datetime.today() + timedelta(hours=expiration_hours)
        return cls.token_model.create(user_id, 'auth', expiration=expiration).token

    @classmethod
    def create_reset_token(cls, user_id):
        # TODO take expiration hours out of here and put it into
        # app configuration
        expiration_hours = 2 * 24 # two days
        expiration = datetime.today() + timedelta(hours=expiration_hours)
        entity = cls.token_model.create(user_id, 'reset', expiration=expiration, delete_past_tokens=True)
        return entity.token

    @classmethod
    def validate_reset_token(cls, user_id, token):
        return cls.validate_token(user_id, 'reset', token)

    @classmethod
    def delete_reset_token(cls, user_id, token):
        cls.token_model.get_key(user_id, 'reset', token).delete()

    @classmethod
    def delete(cls, key):
        if not isinstance(key, ndb.Key):
            key = ndb.Key(cls, key)

        instance = key.get()
        if instance:
            # the Unique model does not set the User as its
            # parent, so we need to delete it ourselves
            Unique = webapp2_extras.appengine.auth.models.Unique
            Unique.delete_multi(map(lambda s: 'User.auth_id:' + s, instance.auth_ids))

            # all other children can be deleted by an ancestor query
            ndb.delete_multi(ndb.Query(ancestor=key).iter(keys_only = True))

            instance._key.delete()

    @classmethod
    def descendant_model(cls, role):

        sponsors = {
            'SPONSORT1': SponsorT1,
            'SPONSORT2': SponsorT2,
            'SPONSORT3': SponsorT3,
            'SPONSORT4': SponsorT4,
            'SPONSORT5': SponsorT5
        }

        clazz = None
        if role == 'HACKER':
            clazz = Hacker
        elif role == 'VOLUNTEER':
            clazz = Volunteer
        elif role in sponsors:
            clazz = sponsors.get(role)
        elif role == 'MENTOR':
            clazz = Mentor
        elif role == 'STAFF':
            clazz = Staff
        elif role == 'ADMINISTRATOR':
            clazz = Administrator
        return clazz

    def serialize(self, company=None):
        """
        Serializes user

        returns:
            a dictionary containing all relevant keys and values
        """

        serialization = self.to_dict(exclude=['auth_ids', 'password'])
        return serialization

    def set_password(self, raw_password):
        """
        Sets the password for the current user.
        Doesn't update changes to user in datastore, however.

        :param raw_password:
            The raw password which will be hashed and stored
        """

        self.password = security.generate_password_hash(raw_password, length=12)

    def set_admin_role(self):
        self.role = 'ADMINISTRATOR'

    def set_staff_role(self):
        self.role = 'STAFF'

    def set_mentor_role(self):
        self.role = 'MENTOR'

    def set_sponsor_role(self, tier):
        if not isinstance(tier, int) and not BOTTOM_SPONSOR_TIER <= tier <= TOP_SPONSOR_TIER:
            raise ValueError("The given tier is not available")

        self.role = 'SPONSORT%d' % tier

    def set_volunteer_role(self):
        self.role = 'VOLUNTEER'

    def set_hacker_role(self):
        self.role = 'HACKER'

    def has_role(self, requested_role):
        """
        Checks to see if user has the single requested role

        args:
            requested_role: a string representing a role
        returns:
            True if the user has the requested role, False otherwise
        raises:
            ValueError if requested_role is not in ROLE_OPTIONS
        """
        if requested_role not in ROLE_OPTIONS:
            raise ValueError("The requested role [%s] is not a valid option" % requested_role)

        existing_role = self.role
        if not existing_role:
            return False
        return existing_role == requested_role

    def has_roles(self, requested_roles=['ADMINISTRATOR', 'STAFF', 'MENTOR',
        'SPONSORT1', 'SPONSORT2', 'SPONSORT3', 'SPONSORT4', 'SPONSORT5']):
        """
        Checks to see if user has any of the requested roles

        args:
            requested_role: a list of strings representing roles.
            If this is not specified, then all roles excluding HACKER are
            used instead
        returns:
            True if the user has any of the requested roles, False otherwise
        raises:
            ValueError if any of the requested_roles are not in ROLE_OPTIONS
        """
        for requested_role in requested_roles:
            if requested_role not in ROLE_OPTIONS:
                raise ValueError("The requested role [%s] is not a valid option" % requested_role)

        existing_role = self.role
        if not existing_role:
            return False
        return existing_role in requested_roles

    def has_permission(self, permission):
        """
        Looks through the list of permissions to see
        if the requested one exists

        args:
            permission: a permission object (either
            constructed partially or retrieved from
            the datastore)
        returns:
            whether or not the permission was found
        """

        for p in self.permissions:
            if p.scope == permission.scope and p.target == permission.target and \
                p.permission == permission.permission:
                return True
        return False

    def descendant(self, create=False):
        """
        Retrieves the primary descendant for the User,
        as determined by the User's role

        args:
            create (optional): create (but do not save) an appropriate
            instance of the descendant if one does not exist
            Defaults to False

        returns:
            A Hacker, Volunteer, SponsorT[1-5], Mentor, Staff,
            or Administrator model, otherwise None
        """

        key = self._key
        clazz = User.descendant_model(self.role)
        result = None
        if clazz:
            result = clazz.query(ancestor=key).fetch(1)

        if not clazz:
            return None
        if create and not result:
            return clazz(parent=self._key)
        return result[0] if result else None
