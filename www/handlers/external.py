from www.handlers.base import BaseHandler

class TravelInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/travel.html", data={})

class ProjectsInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/projects.html", data={})

class JudingInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/judging.html", data={})

class MapsInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/maps.html", data={})

class PrizesInfoHandler(BaseHandler):
	def get(self):
		self.render("templates/prizes.html", data={})

class APIInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/apis.html", data={})

class HardwareInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/hardware.html", data={})

class DayOfInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/day-of.html", data={})

class MentorInfoHandler(BaseHandler):
    def get(self):
        self.render("templates/mentor.html", data={})