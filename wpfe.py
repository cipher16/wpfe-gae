from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Controllers.WPAdmin import *
from Controllers.RSSContentUpdater import RssContentUpdater
from Controllers.Dispatcher import *
import os

#blog configuration
BLOG_URL   = "http://blog.gaetan-grigis.eu"
BLOG_NAME  = "Le Blog du Grand Loup Zeur"
BLOG_DESCR = "le blog qui vous apprend ce que vous savez deja"
BLOG_FEED  = "http://feeds.feedburner.com/LeBlogDuGrandLoupZeur"
BLOG_ABOUT = "Blog d'un etudiant en informatique"

FEED_REFRESH = 36000 #in minutes
NB_ARTICLE_HOME = 10 #numbers of articles to display per page

#template, don't touch this if you haven't modified a template
APPLICATION_PATH = os.path.dirname(__file__)
TEMPLATE = APPLICATION_PATH+"/Views/default"


#do not touch below or die in hell ;)
application = webapp.WSGIApplication(
    [
     #administration part
      ('/admin/upload',WPUploader),                    #import 100%
      ('/admin/import',WPImporter),                    #import 100% 
      ('/admin/rssUpdate', RssContentUpdater),         #50% parsing OK, need DB insertion + cron
      ('/admin/.*',WPAdmin),                     
     #blog part
      ('/', Home),                  #display several articles OK 100%
      ('/page/.*', Home),           #display page contents    OK 100%
      ('/tag/.*', TagsAndCats),     #archive system                0%
      ('/category/.*', TagsAndCats),#archive system                0%
      ('/feed/.*', Feed),           #feed generator                0% recuperation depuis la base de données ?
      ('/.*', Dispatcher)           #display single article   OK 100%
    ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
