import re, logging, json, datetime

from www import utils
from www.models import User, UserToken
from www.handlers.base import BaseHandler
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError

class LoginHandler(BaseHandler):
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
        else:
            data["errors"]["email"] = 'This value is required'

        if password:
            if len(password) < 8:
                data["errors"]["password"] = "This value must be at least 8 characters"
        else:
            data["errors"]["password"] = "This value is required"

        if data["errors"]:
            self.write_json(json.dumps(data))
            return

        user = None
        try:
            email = email.lower()
            user = self.auth.get_user_by_password(email, password)
        except InvalidAuthIdError:
            data["errors"]["email"]= "No user exists with this email."
            self.write_json(json.dumps(data))
            return

        except InvalidPasswordError:
            data["errors"]["password"]= "This password is incorrect."
            self.write_json(json.dumps(data))
            return

        user = User.get_by_id(user['user_id'])
        if not user:
            # this should never happen, but just to be safe
            data["redirect"] = self.uri_for('authenticate')
        elif user.has_roles(['ADMINISTRATOR', 'STAFF']):
            data["redirect"] = self.uri_for('admin_home')
        elif user.has_role('HACKER'):
            data["redirect"]= self.uri_for('register')
        else:
            data["errors"]["email"] = "Sorry, but you cannot authenticate here"
            self.auth.unset_session()

        self.write_json(json.dumps(data))

class LogoutHandler(BaseHandler):
    def get(self):
        self.auth.unset_session()

class ResetPasswordHandler(BaseHandler):
    def get(self):
        data = {}
        data["errors"] = {}

        reset_token = self.request.get("token")
        user_id = self.request.get("user")

        user_token = self.user_model.validate_token(int(user_id), 'reset', reset_token)

        if not user_token:
            self.abort(404)
            return

        params = {
            'user': user_id,
            'token': reset_token
        }
        self.render('templates/password_reset.html', data=params)

    def post(self):
        parameters = self.request.POST
        email = parameters.getone("email")
        password = parameters.getone("password")
        reset_token = parameters.getone("token")
        data = {}
        data["errors"] = {}
        data["messages"] = {}

        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                data["errors"]["email"] = "This value must be a valid email address"
        else:
            data["errors"]["email"] = 'This value is required'

        if password:
            if len(password) < 8:
                data["errors"]["password"] = "This value must be at least 8 characters"
        else:
            data["errors"]["password"] = "This value is required"

        if data["errors"]:
            self.write_json(json.dumps(data))
            return

        email = email.lower()
        user = self.user_model.get_by_auth_id(email)

        if not user:
            data["errors"]["email"] = "No user exists with this email."
            self.write_json(json.dumps(data))
            return

        user_id = user.get_id()
        has_token = self.user_model.validate_token(int(user_id), 'reset', reset_token)

        if not has_token:
            data["errors"]["email"] = "This account doesn't have the token specified."
            self.write_json(json.dumps(data))
            return

        user.set_password(password)
        user_token_key = self.user_model.token_model.get_key(int(user_id), 'reset', reset_token)

        user_token_key.delete()
        user.put()

        data["messages"]["success"] = "Your password has successfully been reset."
        self.write_json(json.dumps(data))
