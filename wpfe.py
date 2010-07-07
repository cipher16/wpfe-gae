from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Controllers.Main import MainPage
from Controllers.RSSContentUpdater import RssContentUpdater

application = webapp.WSGIApplication([('/', MainPage),('/rssUpdate', RssContentUpdater) ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
