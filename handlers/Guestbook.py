import logging

__author__ = 'owner'


import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from models.Greeting import Greeting
from models.Author import Author
import webapp2
from GuestLanding import guestbook_key
import GuestLanding

class Guestbook(webapp2.RequestHandler):

    def get(self):
        #Added to see if I need A get
        logging.info("Help I'm Trapped!")

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          GuestLanding.get_guestbook_key())

        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
