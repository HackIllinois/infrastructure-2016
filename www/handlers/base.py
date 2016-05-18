import os
import jinja2
import webapp2
import pickle
import logging
import datetime

import urllib
from google.appengine.ext import ereporter

from google.appengine.api import users

from google.appengine.api import memcache

import json
import datetime

from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras import security

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from www import models, utils

# TODO: clean this (and the rest of this file) up
template_dir = os.path.join(os.path.dirname(__file__), os.pardir)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
jinja_env.filters.update({
        'is_list': lambda l: isinstance(l, list),
        'first': lambda l: l[0] if len(l) else None,
        'group_by_scope': lambda perms, scope: [p for p in perms if p['scope'] == scope],
        'group_by_name': lambda perms, name: [p for p in perms if p['permission'] == name],
        'group_by_target': lambda perms, target: [p for p in perms if p['target'] == target],
        'epoch_milliseconds': lambda dt: utils.to_epoch_seconds(dt)
    })

#https://developers.google.com/appengine/articles/python/recording_exceptions_with_ereporter
ereporter.register_logger()

class BaseHandler(webapp2.RequestHandler):
    """ This is the Base Handler
        This is the parent of every other handler
        Most other handlers use functions defined in this hander
        This handler is the child of webapp2.RequestHandler which is pre-defined by webapp2"""

    def __init__(self, request, response):
        super(BaseHandler, self).__init__(request, response)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def write_json(self, *a, **kw):
        self.response.headers["Content-Type"] = "application/json"
        self.write(*a, **kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        page = t.render(params)

        return page

    @webapp2.cached_property
    def auth(self):
        """Shortcut to access the auth instance as a property."""
        return auth.get_auth()

    @webapp2.cached_property
    def user_info(self):
        """Shortcut to access a subset of the user attributes that are stored
        in the session.

        The list of attributes to store in the session is specified in
            config['webapp2_extras.auth']['user_attributes'].
        :returns
            A dictionary with most user information
        """
        return self.auth.get_user_by_session()

    @webapp2.cached_property
    def user(self):
        """Shortcut to access the current logged in user.

        Unlike user_info, it fetches information from the persistence layer and
        returns an instance of the underlying model.

        :returns
            The instance of the user model associated to the logged in user.
        """
        u = self.user_info
        user = self.user_model.get_by_id(u['user_id']) if u else None
        if not user:
            authorization = self.request.authorization
            if not authorization:
                return None
            auth_type, token = authorization
            if not token:
                return None
            try:
                auth_token, user_id = token.split('|')
                user_id = long(user_id)
            except ValueError:
                return None
            user_token = self.user_model.validate_auth_token(user_id, auth_token)
            if not user_token:
                return None
            user = self.user_model.get_by_id(user_id)
        return user

    @webapp2.cached_property
    def user_model(self):
        """Returns the implementation of the user model.

        It is consistent with config['webapp2_extras.auth']['user_model'], if set.
        """
        return self.auth.store.user_model

    @webapp2.cached_property
    def session(self):
        """Shortcut to access the current session."""
        return self.session_store.get_session(backend="datastore")

    # this is needed for webapp2 sessions to work
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

class BaseAdminHandler(BaseHandler):
    """
    This is for all /admin pages
    Overrides the dispatch method (called before get/post/etc.)
    Sends 401 (Unauthorized) if user is not an admin
    Ref: http://webapp-improved.appspot.com/guide/handlers.html

    DEPRECATED
    """

    def __init__(self, request, response):
        super(BaseAdminHandler, self).__init__(request, response)

    def get_access(self):
        current_user = self.auth.get_session_data()
        if not current_user:
            return "{}"
        try:
            user = Admin.get_by_id(current_user['user_id'], parent=Admin.get_default_event_parent_key())
            if not user:
                return "{}"
            return json.loads(user.access)
        except:
            return "{}"

    def has_access(self, p):
        #TODO: REDIRECT FROM HERE
        access = self.get_access()
        logging.error(access)
        if access == "{}":
            return "NO USER"
        valid = True
        for x in p:
            try:
                valid = valid and access[x]
            except:
                valid = False
        if valid:
            return "ALLOWED"
        else:
            return "NOT ALLOWED"

    def dispatch(self):
        """TODO: Change to new login system"""
        is_admin = False

        current_user = self.auth.get_session_data()
        logging.error(current_user)
        if not current_user:
            return self.abort(401)
        try:
            user = Admin.get_by_id(current_user['user_id'], parent=Admin.get_default_event_parent_key())
            if not user:
                return self.abort(401)
        except:
            return self.abort(401)

        email = user.email
        domain = email.split('@')[1] if len(email.split('@')) == 2 else None  # Sanity check

        if domain == 'hackillinois.org' or email in constants.OTHER_EMAILS:
            # Parent class will call the method to be dispatched
            # -- get() or post() or etc.
            logging.info('Admin user %s is online.', email)
            super(BaseHandler, self).dispatch()
        else:
            logging.info('%s attempted to access an admin page but was denied.', email)
            return self.abort(401)

class MemcacheHandler:
    """
    TODO: Stress Test Memcache with high volume and large strings
    """

    """http://stackoverflow.com/questions/7111068/split-string-by-count-of-characters"""
    def chunks(self, s, n):
        """Produce `n`-character chunks from `s`."""
        for start in range(0, len(s), n):
            yield s[start:start+n]

    """http://stackoverflow.com/questions/9127982/avoiding-memcache-1m-limit-of-values"""
    def store(self, key, value, chunksize=950000):
        serialized = pickle.dumps(value)
        values = {}
        i = 0
        data_chunks = self.chunks(serialized, chunksize)

        #sets groups of chucks each at most 32 MB
        for chunk in data_chunks:
            values['%s.%s' % (key, i)] = chunk
            i += 1
            if i % 32 == 0:
                memcache.set_multi(values, time=10800)
                values = {}
        if i % 32:
            memcache.set_multi(values, time=10800)
        #sets count of chunks
        memcache.set(key, i)

    """http://stackoverflow.com/questions/9127982/avoiding-memcache-1m-limit-of-values"""
    def retrieve(self, key):
        #gets count of chunks
        #returns None if it can't get count, or count is 0 (no chunks set)
        count = memcache.get(key)

        if count == 0 or count == None:
            return None

        #gets groups of chucks each at most 32 MB and concatinates the chunks
        #returns None if it can't get a chunk
        keys = []
        serialized = ''
        for i in range(count):
            keys.append('%s.%s' % (key, i))
            i += 1
            if i % 32 == 0:
                result = memcache.get_multi(keys)
                for x in range(32):
                    k = '%s.%s' % (key, i+x-32)
                    if k not in result or not result[k]:
                        #Memcache string is invalid
                        return None
                    serialized += result[k]
                keys = []
        if i % 32:
            result = memcache.get_multi(keys)
            for x in range(i%32):
                k = '%s.%s' % (key, i/32*32+x)
                if k not in result or not result[k]:
                    #Memcache string is invalid
                    return None
                serialized += result[k]
        data = None
        if serialized:
            data = pickle.loads(serialized)
        return data

    def set_email_memcache(self):
        data = {}
        emails = Email.search_database()
        for email in emails:
            data[email.email] = {'email': email.email}
        self.store('email', data)
        return data

    def get_email_memcache(self):
        data = self.retrieve('email')
        if data is None:
            logging.info('setting memcache')
            data = self.set_email_memcache()
        return data

    def set_hacker_memcache(self):
        data = []
        users = User.search_database()
        for user in users:
            try:
                data.append({'email':user.email, 'first_name':user.first_name, 'last_name':user.last_name, 'gender':user.gender, 'graduation_year':user.graduation_year, 'major':user.major, 'school':user.school, 'gluten':user.diet.gluten, 'vegetarian':user.diet.vegetarian, 'vegan':user.diet.vegan, 'diet_text':user.diet.other, 'hardware':user.hardware.equipment, 'hardware_check':user.hardware.hack, 'shirt':user.shirt, 'team':user.team, 'url_github':user.url_github, 'url_linkedin':user.url_linkedin, 'url_website':user.url_website, 'resume_link':user.resume.gsObjectName[17:], 'waitlisted':user.status.waitlisted, 'approved':user.status.approved, 'confirmed':user.status.confirmed, 'approvedwave':user.status.approvedwave, 'registration_time':user.registration_time, 'key':user.key.id(), 'rsvp':user.rsvp, 'work':user.work, 'worktype':user.worktype, 'busroutes':user.busroutes})
            except:
                data.append({'email':user.email, 'first_name':user.first_name, 'last_name':user.last_name, 'gender':user.gender, 'graduation_year':user.graduation_year, 'major':user.major, 'school':user.school, 'gluten':user.diet.gluten, 'vegetarian':user.diet.vegetarian, 'vegan':user.diet.vegan, 'diet_text':user.diet.other, 'hardware':user.hardware.equipment, 'hardware_check':user.hardware.hack, 'shirt':user.shirt, 'team':user.team, 'url_github':user.url_github, 'url_linkedin':user.url_linkedin, 'url_website':user.url_website, 'resume_link':user.resume.gsObjectName[17:], 'waitlisted':user.status.waitlisted, 'approved':user.status.approved, 'confirmed':user.status.confirmed, 'approvedwave':user.status.approvedwave, 'registration_time':user.registration_time, 'key':user.key.id(), 'rsvp':user.rsvp, 'work':user.work, 'busroutes':user.busroutes})
        self.store('hacker', data)
        return data

    def get_hacker_memcache(self):
        data = self.retrieve('hacker')
        if data is None:
            logging.info('setting memcache')
            data = self.set_hacker_memcache()
        return data
