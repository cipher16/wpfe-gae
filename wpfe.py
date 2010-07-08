from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Controllers.WPImporter import WPImporter
from Controllers.RSSContentUpdater import RssContentUpdater
from Controllers.Dispatcher import *
import os

BLOG_URL = "http://blog.gaetan-grigis.eu"
NB_ARTICLE_HOME = 10
APPLICATION_PATH = os.path.dirname(__file__)
TEMPLATE = APPLICATION_PATH+"/Views/default"

application = webapp.WSGIApplication(
    [
      ('/admin/import',WPImporter),
      ('/admin/rssUpdate', RssContentUpdater),
      ('/', Home),
      ('/.*', Dispatcher)
    ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
