from webapp2 import Route, RedirectHandler
from webapp2_extras.routes import RedirectRoute
from www.handlers import *

routes = [
    ### Handler Redirects ###
    RedirectRoute('/', handler=index.IndexHandler, name='index', strict_slash=True),
    RedirectRoute('/authenticate', handler=users.SignupHandler, name='authenticate', strict_slash=True),
    # RedirectRoute('/signup', handler=users.SignupHandler, name='signup', strict_slash=True),
    RedirectRoute('/forgot', handler=users.ForgotPasswordHandler, name='forgot', strict_slash=True),
    RedirectRoute('/reset', handler=auth.ResetPasswordHandler, name='reset', strict_slash=True),
    RedirectRoute('/register', handler=users.RegistrationHandler, name='register', strict_slash=True),
    RedirectRoute('/register/complete', handler=users.RegistrationSuccessHandler, name='register_success', strict_slash=True),
    RedirectRoute('/rsvp', handler=users.RSVPHandler, name="rsvp", strict_slash=True),
    RedirectRoute('/login', handler=auth.LoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout', handler=auth.LogoutHandler, name='logout', strict_slash=True),

    RedirectRoute('/tasks/eaccess', handler=tasks.EAccessDeferredHandler, name='eaccess_deferred', strict_slash=True),
    RedirectRoute('/tasks/buschecklist', handler=tasks.BusChecklistDeferredHandler, name='bus_checklist_deferred', strict_slash=True),
    RedirectRoute('/tasks/dashboardstats', handler=tasks.DashboardDeferredHandler, name='dashboard_deferred', strict_slash=True),
	
    RedirectRoute('/admin',  handler=admin.HomeHandler, name='admin_home', strict_slash=True),
    RedirectRoute('/admin/search', handler=admin.SearchHandler, name="admin_search"),
    RedirectRoute('/admin/review/datatable', handler=admin.ReviewDataTableHandler, name='admin_review_table'),
    RedirectRoute(r'/admin/review/<user_id:\d+>', handler=admin.ReviewDetailsHandler, name='admin_review_details', strict_slash=True),
    RedirectRoute('/admin/review', handler=admin.ReviewHandler, name='admin_review', strict_slash=True),
    RedirectRoute(r'/admin/checkin/<user_id:\d+>', handler=admin.CheckinDataHandler, name='admin_checkin_details', strict_slash=True),
    RedirectRoute('/admin/checkin/datatable', handler=admin.CheckinDataTableHandler, name='admin_checkin_table'),
    RedirectRoute('/admin/checkin', handler=admin.CheckinHandler, name='admin_checkin', strict_slash=True),
    RedirectRoute('/admin/users', redirect_to='/admin/users/view', name='admin_user', strict_slash=True),
    RedirectRoute(r'/admin/users/view/<user_id:\d+>', handler=admin.UserViewHandler, name='admin_user_view', strict_slash=True),
    RedirectRoute(r'/admin/users/<mode:(view|add)>', handler=admin.UserManagementHandler, name='admin_user_manage', strict_slash=True),
    RedirectRoute('/admin/network', handler=admin.NetworkCredentialsUploadHandler, name='admin_netcred_upload', strict_slash=True),
    RedirectRoute(r'/admin/notify/<wave:\d+>', handler=admin.SendNotificationWaveHandler, name='admin_notify', strict_slash=True),
    RedirectRoute('/admin/notify', handler=admin.NotificationWaveHandler, name='admin_notify', strict_slash=True),
    RedirectRoute('/admin/dashboard', handler=admin.DashboardHandler, name='admin_dashboard', strict_slash=True),
    RedirectRoute('/admin/hardwaresecret', handler=admin.HardwareSecretHandler, name='admin_hardware_secret', strict_slash=True),

    RedirectRoute(r'/api/v1/users/<user_id:\d+>', handler=endpoints.UsersEndpoint, name='endpoints_users', strict_slash=True),
    RedirectRoute('/api/v1/auth', handler=endpoints.AuthEndpoint, name='endpoints_auth', strict_slash=True),

    RedirectRoute(r'/download/resume/<blobstore_key:([^/]+)?>', handler=common.ResumeDownloadHandler, name='resume_download', strict_slash=True),

    RedirectRoute('/travel', handler=external.TravelInfoHandler, name='travel_info', strict_slash=True),
    RedirectRoute('/transit', redirect_to='/travel', name='transit_redirect', strict_slash=True),
    RedirectRoute('/projects', handler=external.ProjectsInfoHandler, name='projects_info', strict_slash=True),
    RedirectRoute('/judging', handler=external.JudingInfoHandler, name='judging_info', strict_slash=True),
    RedirectRoute('/maps', handler=external.MapsInfoHandler, name='maps_info', strict_slash=True),
    RedirectRoute('/prizes', handler=external.PrizesInfoHandler, name='prizes_info', strict_slash=True),
    RedirectRoute('/api', handler=external.APIInfoHandler, name='api_info', strict_slash=True),
    RedirectRoute('/apis', redirect_to='/api', name='apis_redirect', strict_slash=True),
    RedirectRoute('/hardware', handler=external.HardwareInfoHandler, name='hardware_info', strict_slash=True),
    RedirectRoute('/dayof', handler=external.DayOfInfoHandler, name='day-of_info', strict_slash=True),
    RedirectRoute('/mentor', handler=external.MentorInfoHandler, name='mentor_info', strict_slash=True),

	RedirectRoute('/archive/landing', handler=archive.LandingHandler, name='landing', strict_slash=True),

    ### Permanent Redirects ###
    Route('/devpost', RedirectHandler, defaults={'_uri': 'http://hackillinois2016s.devpost.com'}),
    Route('/teamformation', RedirectHandler, defaults={'_uri': 'http://goo.gl/pMD1n8'}),

    #RedirectRoute('/401', handler=www.error.handlers.Error401Handler, name='Error401', strict_slash=True),
    #RedirectRoute('/404', handler=www.error.handlers.Error404Handler, name='Error404', strict_slash=True),
]

error_handlers = {
    #401: www.error.handlers.handle401,
    #404: www.error.handlers.handle404,
}
