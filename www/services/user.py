import uuid

from www.services.mail import MailService
from www import models, services

ADMIN_ROLES = ['ADMINISTRATOR']
HELPQ_MENTOR_ROLES = ['MENTOR', 'STAFF','SPONSORT1','SPONSORT2','SPONSORT3','SPONSORT4','SPONSORT5']
ORGANIZATIONAL_ROLES = ['MENTOR','SPONSORT1','SPONSORT2','SPONSORT3','SPONSORT4','SPONSORT5']
HELPQ_COMMON_ROLES = ['HACKER']
SCANNING_ROLES = ['STAFF', 'SPONSORT2','SPONSORT3','SPONSORT4','SPONSORT5']
CHECK_IN_ROLES = ['STAFF']
HARDWARE_CHECKOUT_ROLES = ['STAFF']

PRETTY_ROLES = {
    "ADMINISTRATOR": "Administrator",
    "STAFF": "Staff Member",
    "SPONSORT1": "Sponsor",
    "SPONSORT2": "Sponsor",
    "SPONSORT3": "Sponsor",
    "SPONSORT4": "Sponsor",
    "SPONSORT5": "Sponsor",
    "MENTOR": "Mentor",
    "VOLUNTEER": "Volunteer",
    "HACKER": "Hacker"
}

class UserException(Exception):
    """
    Base class for user-related exceptions.
    """
    name = "UserCreationException"

class MissingRequiredParameter(UserException):
    """
    Raised when the UserService isn't supplied all required parameters.
    """
    name = "MissingRequiredParameterError"

class UserNotFound(UserException):
    """
    Raised when a user is not found in a query.
    """
    name = "UserNotFoundError"

class UserAlreadyExists(UserException):
    """
    Raised when one attempts to overwrite an existing user.
    """
    name = "UserAlreadyExistsError"

class UserService(object):
    """
    The UserService implements the functionality
    required to add users of any kind and address
    their roles, permissions, and company, as needed.
    """

    def __init__(self, app):
        """
        Creates a new UserService
        args:
            app: the current app
        """
        self.mail_service = MailService(app)

    def _generate_password(self):
        return uuid.uuid4().hex

    def _permission_exists(self, permission_list, permission):
        existing = [p for p in permission_list if p.permission == permission.permission \
            and p.scope == permission.scope and p.target == permission.target]
        return len(existing) > 0

    def send_new_user_email(self, host_url, reset_token, user):
        reset_url = host_url + "/reset?user=" + str(user.get_id())
        reset_url = reset_url + "&token=" + reset_token

        subject = "Your HackIllinois Account"
        body = "Hi,\n\nYou've been added to HackIllinois as a %s. " % PRETTY_ROLES.get(user.role, 'new member')
        body += "To set your password, use the link below:\n%s"
        body = body % reset_url
        if user.role not in ORGANIZATIONAL_ROLES:
            body += "\n\nAs a HackIllinois participant, you'll also need to complete your registration information as soon as possible. After creating a new password, please log in and complete the form."
        body += "\n\nThanks,\n- HackIllinois Systems"
        self.mail_service.send(user.email, subject, body)

    def add_admin_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.*')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_admin_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.*']
        return permissions_list

    def add_helpq_mentor_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.helpq.mentor')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_helpq_mentor_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.helpq.mentor']
        return permissions_list

    def add_helpq_common_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.helpq.common')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_helpq_common_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.helpq.common']
        return permissions_list

    def add_scan_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.users.scanning')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_scan_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.users.scanning']
        return permissions_list

    def add_checkin_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.users.checkin')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_checkin_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.users.checkin']
        return permissions_list

    def add_hardware_checkout_permission(self, permission_list, role):
        permission = models.Permission.add_role_permission(role, 'hackillinois.hardware.checkout')
        if (self._permission_exists(permission_list, permission)): return permission_list

        permission_list.append(permission)
        return permission_list

    def remove_hardware_checkout_permission(self, permission_list):
        permissions_list = [p for p in permission_list if p.permission != 'hackillinois.hardware.checkout']
        return permissions_list

    def get_permissions_for_role(self, role):
        """
        Compiles all permissions that apply to a specific role
        args:
            role: a string representing a valid role
        returns:
            a ist of the permissions that apply to the given role
        """

        permissions = []
        if role in ADMIN_ROLES:
            permissions = self.add_admin_permission(permissions, role)

        if role in HELPQ_MENTOR_ROLES:
            permissions = self.add_helpq_mentor_permission(permissions, role)

        if role in HELPQ_COMMON_ROLES:
            permissions = self.add_helpq_common_permission(permissions, role)

        if role in SCANNING_ROLES:
            permissions = self.add_scan_permission(permissions, role)

        if role in CHECK_IN_ROLES:
            permissions = self.add_checkin_permission(permissions, role)

        if role in HARDWARE_CHECKOUT_ROLES:
            permissions = self.add_hardware_checkout_permission(permissions, role)

        return permissions

    def get_permissions_for_organization(self, organization):
        organization_id = organization.key.id()
        organization_permissions = models.Permission.query(models.Permission.target == str(organization_id)).fetch()
        return organization_permissions


    def create_user(self, parameters, create_descendant=True):
        properties = models.User._properties
        user_allowed = list(properties)
        user_required = [p for p in user_allowed if properties.get(p)._required and properties.get(p)._default == None]
        user_creation_parameters = {key: value for (key, value) in parameters.iteritems() if key in user_allowed}
        if not all (p in user_creation_parameters for p in user_required):
            raise MissingRequiredParameter("Missing the following required parameters: %r" % [str(x) for x in user_required if x not in user_creation_parameters])

        #Roles are required, so we must have one
        role = user_creation_parameters.get('role')

        if role not in models.ROLE_OPTIONS:
            raise ValueError("Invalid value for parameter, 'role': %s" % role)

        # We only need to check these if a descendant will be created later
        if create_descendant:
            descendant_model = models.User.descendant_model(role)
            descendant_properties = descendant_model._properties
            descendant_allowed = list(descendant_properties)
            descendant_required = [p for p in descendant_allowed if descendant_properties.get(p)._required and descendant_properties.get(p)._default == None]
            descendant_creation_parameters = {key: value for (key, value) in parameters.iteritems() if key in descendant_allowed}
            if not all (p in descendant_creation_parameters for p in descendant_required):
                raise MissingRequiredParameter("Missing the following required parameters: %r" % [str(x) for x in descendant_required if x not in descendant_creation_parameters])

        email = user_creation_parameters.get('email')
        del user_creation_parameters['email']

        password = parameters.get('password_raw')
        if not password:
            password = self._generate_password()
        user_creation_parameters['password_raw'] = password


        permissions = self.get_permissions_for_role(role)
        if role in ORGANIZATIONAL_ROLES:
            organization = parameters.get('organization')
            organization_permissions = self.get_permissions_for_organization(organization)
            permissions.extend(organization_permissions)
        user_creation_parameters['permissions'] = permissions

        successful, user = models.User.create_user(email, **user_creation_parameters)

        if not successful:
            raise UserAlreadyExists("A user with the requested email already exists")

        if not create_descendant:
            #Then we are done, and we can return the user.
            return user

        descendant = user.descendant(create=True)
        for key, value in descendant_creation_parameters.iteritems():
            setattr(descendant, key, value)
        descendant.put()

        return user

    def update_user(self, parameters, id):
        user = models.User.get_by_id(id)

        if not user:
            raise UserNotFound('A user with the id, %r, doesn\'t exist.' % id)

        properties = user._properties
        user_allowed = list(properties)
        user_update_parameters = {key: value for (key, value) in parameters.iteritems() if key in user_allowed}
        for key, value in user_update_parameters.iteritems():
            setattr(user, key, value)
        user.put()

        descendant = user.descendant()

        descendant_properties = descendant._properties
        descendant_allowed = list(properties)
        descendant_update_parameters = {key: value for (key, value) in parameters.iteritems() if key in descendant_allowed}
        for key, value in descendant_update_parameters.iteritems():
            setattr(descendant, key, value)
        descendant.put()

        return user
