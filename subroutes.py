__author__ = 'owner'

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import webapp2
from webapp2_extras import routes
import handlers

#subroutes = [
#    webapp2.Route(r'/.*',
#            handlers.main),
#]

application = webapp2.WSGIApplication([
    ('/', handlers.Main),
    ('/guestbook', handlers.GuestLanding),
    ('/sign?.*', handlers.Guestbook),
    ], debug=True)


## Runs the admin application.
#
def main():
    application.run()

if __name__ == '__main__':
    main()

