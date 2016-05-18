import re, json
from www.handlers.base import BaseHandler
from www import errors, response_utils, utils
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError

class AuthEndpoint(BaseHandler):
    def post(self):
        parameters = json.loads(self.request.body)
        parameters = utils.pythonize(dict(parameters))
        email = parameters.get("email")
        password = parameters.get("password")
        response = None

        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                response = response_utils.make_error(errors.InvalidParameterError("This value must be a valid email address", 'email'))
        else:
            response = response_utils.make_error(errors.MissingParameterError("Missing required parameter: \'email\'", 'email'))

        if password:
            if len(password) < 8:
                response = response_utils.make_error(errors.InvalidParameterError('Passwords cannot be less than 8 characters long.', 'password'))
        else:
            response = response_utils.make_error(errors.MissingParameterError("Missing required parameter: \'password\'", 'password'))

        if response:
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return

        user = None
        try:
            email = email.lower()
            user = self.user_model.get_by_auth_password(email, password)
        except InvalidAuthIdError:
            response = response_utils.make_error(errors.NotFoundError("No user exists with this email.", 'email'))
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return

        except InvalidPasswordError:
            response = response_utils.make_error(errors.UnauthenticatedRequestError("This password is incorrect.", 'password'))
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return

        user_id = user.get_id()
        token = self.user_model.create_auth_token(user_id)

        if not token:
            # this should never happen, but just to be safe
            response = response_utils.make_error(errors.NotFoundError("No user exists with this email.", 'email'))
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return

        token += '|' + str(user_id)
        response = response_utils.make_response({'userId': user_id, 'token': token })
        self.response.set_status(response['meta']['status'])
        self.write_json(json.dumps(response))

class UsersEndpoint(BaseHandler):
    def get(self, user_id):
        REGISTERED_PERSON_ROLES = ['HACKER', 'ADMINISTRATOR', 'STAFF']
        subject_id = long(user_id)
        user = self.user
        if not user:
            response = response_utils.make_error(errors.UnauthenticatedRequestError("Not authenticated.", 'user'))
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return
        user_role = user.role
        user_id = user.get_id()
        #If user is not requesting themselves
        if not subject_id == user_id:
            #Hackers cannot access other user's information
            if user_role == "HACKER":
                response = response_utils.make_error(errors.UnauthorizedRequestError(None, 'role'))
                self.response.set_status(response['meta']['status'])
                self.write_json(json.dumps(response))
                return
            subject = self.user_model.get_by_id(subject_id)
            if not subject:
                response = response_utils.make_error(errors.NotFoundError("No user exists with this id.", 'user_id'))
                self.response.set_status(response['meta']['status'])
                self.write_json(json.dumps(response))
                return
        else:
            subject = user

        subject_role = subject.role
        serialized_user = subject.serialize()
        descendant = subject.descendant()
        if not descendant:
            # In case someone who hasn't registered is requested
            response = response_utils.make_response(serialized_user)
            self.response.set_status(response['meta']['status'])
            self.write_json(json.dumps(response))
            return

        serialized_descendant = descendant.serialize()

        if user_role == 'HACKER' and user_id == subject_id:
            # This only happens if a hacker is requesting themselves
            del serialized_descendant['status']
            del serialized_descendant['reviewer']

        serialized_user['descendant'] = serialized_descendant
        response = response_utils.make_response(serialized_user)
        self.response.set_status(response['meta']['status'])
        self.write_json(json.dumps(response))
