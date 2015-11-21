# [START imports]
import os

import jinja2
import settings
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
from models.Greeting import Greeting
from models.Author import Author
import webapp2

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

template_loader = jinja2.FileSystemLoader(settings.TEMPLATE_DIR)
JINJA_ENVIRONMENT = jinja2.Environment(loader=template_loader)
# [END imports]

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.
    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

def get_guestbook_key():
    return guestbook_key()

# [START main_page]
class GuestLanding(webapp2.RequestHandler):

    baseLink = {'link': '/', 'label': 'Home'}

    def get(self, request=webapp2.RequestHandler):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        context = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }
        # _link = baselink[link] +
        _resp = JINJA_ENVIRONMENT.get_template('static/guestbook.html')
        self.response.write(_resp.render(context))

    def post(self, request=webapp2.RequestHandler):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name', get_guestbook_key())

        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()
        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/guestbook/sign?' + urllib.urlencode(query_params))


# [END main_page]





