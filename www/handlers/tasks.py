import www.deferreds as deferreds

from www.handlers.base import BaseHandler

from google.appengine.api import memcache
from google.appengine.ext import deferred

class BaseTaskHandler(BaseHandler):
	"""
	Provides framework for handling deferred tasks
	"""

	# the default task result expiration is 1 hour
	TASK_EXPIRATION_IN_SECONDS = 3600
	# the default task key is absent and should be set by the implementer
	TASK_CACHE_KEY = None

	def _is_requisite(self):
		"""
		Ensures that the related task is ready to be executed. Often, this
		includes checking the cache for previous runs and/or results
		"""
		return memcache.get(self.TASK_CACHE_KEY) is None

	def _execute(self):
		"""
		Handles the related task
		"""
		raise NotImplementedError("Task handlers must override _execute")

	def _set_executed(self):
		"""
		Indicates that the task has been executed, typically by setting
		a key in the cache
		"""
		memcache.add(key=self.TASK_CACHE_KEY, time=self.TASK_EXPIRATION_IN_SECONDS, value=True)

	def get(self):
		if not self._is_requisite():
			return self.abort(304)

		self._execute()
		self._set_executed()
		self.response.out.write("Task started")

class EAccessDeferredHandler(BaseTaskHandler):

	# the eaccess data can usually be stale for a while, so we
	# keep the expiration at 6 hours
	TASK_EXPIRATION_IN_SECONDS = 6 * 3600
	TASK_CACHE_KEY = 'EACCESS_TASK_RUN'

	def _execute(self):
		app = self.app.config
		root_url = self.request.host_url
		deferred.defer(deferreds.SponsorEAccessDeferred, app_config=app, root_url=root_url)

class BusChecklistDeferredHandler(BaseTaskHandler):

	# the bus data can usually be stale for a while, so we
	# keep the expiration at 6 hours
	TASK_EXPIRATION_IN_SECONDS = 6 * 3600
	TASK_CACHE_KEY = 'BUS_CHECKLIST_TASK_RUN'

	def _execute(self):
		app = self.app.config
		deferred.defer(deferreds.BusChecklistDeferred, app_config=app)

class AttendeeListDeferredHandler(BaseTaskHandler):

	# TODO: remove this task (it should be replaced by a mailing list that is
	# created automatically based on people who are checked in)

	# the attendee data can usually be stale for a while, so we
	# keep the expiration at 6 hours
	TASK_EXPIRATION_IN_SECONDS = 6 * 3600
	TASK_CACHE_KEY = 'ATTENDEES_TASK_RUN'

	def _execute(self):
		app = self.app.config
		deferred.defer(deferreds.AttendeeListDeferred, app_config=app)

class DashboardDeferredHandler(BaseTaskHandler):

	# the dashboard data is usually pinged often, so we
	# keep the expiration at 15 minutes
	TASK_EXPIRATION_IN_SECONDS = 15 * 60
	TASK_CACHE_KEY = 'DASHBOARD_TASK_RUN'

	def _execute(self):
		deferred.defer(deferreds.DashboardStatsDeferred)
