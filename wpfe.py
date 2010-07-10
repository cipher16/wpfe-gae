from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Controllers.WPImporter import *
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
      ('/admin/upload',WPUploader),                    #import 0%
      ('/admin/import',WPImporter),                    #import 100% 
      ('/admin/rssUpdate', RssContentUpdater),         #50% parsing OK, need DB insertion + cron
      ('/', Home),           #display several articles OK 100%
      ('/page/.*', Home),    #display page contents    OK 100%
      ('/tag/.*', Home),     #archive system                0%
      ('/category/.*', Home),#archive system                0%
      ('/feed/.*', Home),    #feed generator                0%
      ('/.*', Dispatcher)    #display single article   OK 100%
    ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
