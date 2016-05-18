from www.handlers.base import BaseHandler

class LandingHandler(BaseHandler):
    def get(self):
        self.render("templates/archive/landing.html", data={})
