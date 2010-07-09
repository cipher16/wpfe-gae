from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Controllers.WPImporter import WPImporter
from Controllers.RSSContentUpdater import RssContentUpdater
from Controllers.Dispatcher import *
import os

BLOG_URL   = "http://blog.gaetan-grigis.eu"
BLOG_NAME  = "Le Blog du Grand Loup Zeur"
BLOG_DESCR = "le blog qui vous apprend ce que vous savez deja"
BLOG_FEED  = "http://feeds.feedburner.com/LeBlogDuGrandLoupZeur"

NB_ARTICLE_HOME = 10
APPLICATION_PATH = os.path.dirname(__file__)
TEMPLATE = APPLICATION_PATH+"/Views/default"

application = webapp.WSGIApplication(
    [
      ('/admin/import',WPImporter),
      ('/admin/rssUpdate', RssContentUpdater),
      ('/', Home),
      ('/page/.*', Home),
      ('/tag/.*', Home),
      ('/category/.*', Home),
      ('/.*', Dispatcher)
    ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
