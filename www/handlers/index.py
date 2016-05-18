from www.handlers.base import BaseHandler
import urllib, logging
import re
import random

class IndexHandler(BaseHandler):
    def get(self):
        self.render("templates/index.html")
