#!/usr/bin/env python

import os, random, string, logging
import webapp2

from google.appengine.api.app_identity import app_identity

from www import models
from www import routing

# patch json module
import json, datetime
def defaultEncoder(self, obj):
	if not obj:
		return None
	if isinstance(obj, datetime.datetime):
		return (obj - datetime.datetime(1970,1,1)).total_seconds() * 1000
	if hasattr(obj, '__str__'):
		return obj.__str__()
json.JSONEncoder.default = defaultEncoder

logging.info("Configuring App Engine instance")

# environment variables are set via app.yaml
is_development = os.getenv('IS_DEVELOPMENT', 'TRUE')
is_development = True if is_development == 'TRUE' else False
debug = is_development

logging.info("Creating application-specific configuration")

# create the configuration to inject into the WSGIApplication
app_config = {
	'development': is_development,
	'webapp2_extras.auth': {
		'user_model': 'www.models.User',
		'user_attributes': []
	},
	'webapp2_extras.sessions': {
		'secret_key': None
	},
	'services.mail': {
		'mailgun_domain': 'hackillinois.org',
		'mailgun_secret': os.getenv('MAILGUN_SECRET', 'NONE'),
		'dev_whitelist': ['@hackillinois.org']
	},
	'services.storage': {
		'resume_bucket': '2016-hackillinois-resumes',
		'public_bucket': '2016-hackillinois-public'
	},
	'hardware_api': {
		'secret_key': os.getenv('HARDWARE_SECRET', 'NONE')
	}
}

logging.info("Debug parameter is %r" % (debug))

# generic development setup
if is_development:
	logging.warning("This application is running in development. As such, debugging information will be visible to end-users, and only sandboxed resources will be used.")

	app_config['services.mail']['mailgun_domain'] = 'sandboxcdef5b02a79843feb5e5216dca5edf3c.mailgun.org'
	app_config['services.storage']['resume_bucket'] = '2016-hackillinois-development-resumes'
	app_config['services.storage']['public_bucket'] = '2016-hackillinois-development-public'

	# set up console support for pdb
	import sys
	for attr in ('stdin', 'stdout', 'stderr'):
		setattr(sys, attr, getattr(sys, '__%s__' % attr))

# extract the environment configuration and the admin
# user
admin_id = os.getenv('ADMIN_ID', 'NO-REPLY@HACKILLINOIS.ORG')
env_config = models.Configuration.query().fetch(1)
admin_user = models.User.query().filter(admin_id.lower() == models.User.email).fetch(1)
if not env_config or not admin_user:

	logging.info("Either the environment configuration or the default admin user was not found")
	logging.info("Re-creating both entities")

	# if there's already an config, that means we need to recreate it
	# after we generate an administrator password
	if env_config:
		models.Configuration._clear()
		env_config = []

	env_config = models.Configuration()
	env_config.admin_password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(21))
	env_config.session_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(37))
	env_config.put()

	# set the session secret, since we have only just generated it
	app_config['webapp2_extras.sessions']['secret_key'] = str(env_config.session_secret)

	# remove the current admin (if it exists),
	# since we have a new password
	if admin_user:
		models.User.delete(admin_user[0]._key)
		admin_user = []

	if not admin_user:
		# TODO: find a way to centralize permission creation
		role = 'ADMINISTRATOR'
		role_permission = models.Permission.add_role_permission(role, 'hackillinois.*')
		permissions = [role_permission]
		_, admin_user = models.User.create_user(admin_id, role=role, permissions=permissions,
			password_raw=env_config.admin_password)

		administrator = models.Administrator(parent=admin_user._key)
		administrator.first_name = 'Admin'
		administrator.last_name = 'User'
		administrator.put()

else:
	logging.info("The environment configuration and default admin user were found")
	logging.info("Retaining previous entities")

	# the session secret is the only value that we don't know
	# if an environment configuration already exists
	env_config = env_config[0]
	app_config['webapp2_extras.sessions']['secret_key'] = str(env_config.session_secret)

logging.info("Finishing configuration")
app = webapp2.WSGIApplication(routing.routes, debug=debug, config=app_config)
logging.info("Configuration complete. Application instantiated")

for error in routing.error_handlers:
	app.error_handlers[error] = routing.error_handlers[error]
