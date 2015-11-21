# [START imports]
import base64
import logging
import os
import pickle

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
    messages = None
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
        self.loadMessages()
        context = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
            'messages' : self.messages,
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
        if greeting.author != None:
            greeting.content = self.request.get('content')
            greeting.put()
        else:
            logging.info("hi")
            self.addMessage("You must login before posting.",'Error')
            self.saveMessages()
        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/sign?' + urllib.urlencode(query_params))

    ## Adds Message to queue
    def addMessage(self, message, messageType='info'):
        if not self.messages:
            self.messages = []
        self.messages.append({'message':message, 'type':messageType})

    ## Store messages in a cookie for redirects.
    #
    def saveMessages(self):
        if not self.messages:
            return
        _pickled = pickle.dumps(self.messages)
        _encoded = base64.b64encode(_pickled)
        _cookie = 'msg=%s;path=/;' % _encoded
        self.response.headers.add_header('Set-Cookie', _cookie)
    ## Loads messages from a cookie.
    #
    def loadMessages(self):
        _encoded = self.request.cookies.get('msg')
        if not _encoded:
            # no messages to load
            return
        # clear cookie a decode
        self.response.delete_cookie('msg')
        _pickled = base64.b64decode(_encoded)
        _messages = pickle.loads(_pickled)
        if not isinstance(_messages, list):
            # security check 1, pickled data must be a list
            return
        self.messages = []
        for _message in _messages:
            # security checks:
            # each element must be a dict
            # each dict must have 'type' and 'message'
            # 'type' and 'message' must be strings
            if (isinstance(_message, dict)
                and len(_message) == 2
                and 'type' in _message
                and 'message' in _message
                and isinstance(_message['type'], basestring)
                and isinstance(_message['message'], basestring)
                ):
                # add message from cookie
                self.messages.append(_message)
        return
# [END main_page]





