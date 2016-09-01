__author__ = 'owner'


# [START imports]
import os
import urllib

from google.appengine.api import users

import jinja2
import webapp2
import settings


template_loader = jinja2.FileSystemLoader(settings.TEMPLATE_DIR)
JINJA_ENVIRONMENT = jinja2.Environment(loader=template_loader)
# [END imports]

# [START main_page]
class Main(webapp2.RequestHandler):

    baseLink = {'link': '/', 'label': 'Home'}

    def get(self):
        context = {
        }
        _resp = JINJA_ENVIRONMENT.get_template('static/index.html')
        self.response.write(_resp.render(context))

# [END main_page]
