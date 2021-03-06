from google.appengine.ext import webapp
from Lib.WordPress import *
from google.appengine.ext.webapp import template
import wpfe
from google.appengine.api import memcache
from Lib import RSS, DateTime, Twitter

#type : 
#    home (display 10)
#    single (display 1)
#    page (display a page)

class Home(webapp.RequestHandler):
    def get(self):
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.out.write(data)
            return 
        
        page=1
        if self.request.path.startswith("/page/"):
            page=self.request.path.split("/")
            if len(page)<3:
                page=0
            else:
                page=int(page[2])
            
        ar = WPArticles.getArticles(wpfe.NB_ARTICLE_HOME,(page-1)*wpfe.NB_ARTICLE_HOME)
        template_values = {
           'articles': ar,
           'ParentTmpl': wpfe.TEMPLATE+"/index.html",
           'home':True,
           'blog_name':wpfe.BLOG_NAME,
           'blog_descr':wpfe.BLOG_DESCR,
           'blog_feed':wpfe.BLOG_FEED,
           'blog_about':wpfe.BLOG_ABOUT,
           'archives': WPArticles.getArticles(5,0),
           'categories':WPCategory.getCategories(),
           'twitter':wpfe.TWITTER_LOGIN,
           'page':page,
           'nxtPage': (int(page)+1),
           'prvPage': (int(page)-1),
           'nbArticles':len(ar)
        }
        path = wpfe.TEMPLATE+"/home.html"
#saving memcache
        render = template.render(path, template_values)
        if len(ar)>0 and wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+self.request.path,render)
        self.response.out.write(render)
            
class Dispatcher(webapp.RequestHandler):
    def get(self):
        #memcache system
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.out.write(data)
            return 
        
        #retrieving data
        ar = WPArticles.getArticleByUrl(self.request.path)        
        if not ar:
            self.error(404)
            return
        pr = WPArticles.getPrevArticles(ar.idP, 1)
        nx = WPArticles.getNextArticles(ar.idP, 1)
        if len(pr)>0:
            pr=pr[0]
        if len(nx)>0:
            nx=nx[0]
        ar.category=WPCategory.genUrl(ar.cats)
        ar.tagsURL=WPTags.genUrl(ar.tags)
        
        template_values = {
            'article': ar,
            'title':ar.title,
            'ParentTmpl': wpfe.TEMPLATE+"/index.html",
            'blog_name':wpfe.BLOG_NAME,
            'blog_descr':wpfe.BLOG_DESCR,
            'blog_feed':wpfe.BLOG_FEED,
            'blog_about':wpfe.BLOG_ABOUT,
            'archives': WPArticles.getArticles(5,0),
            'twitter':wpfe.TWITTER_LOGIN,
            'categories':WPCategory.getCategories(),
            'single':True,
            'nextArticle':nx,
            'prevArticle':pr
        }
        path = wpfe.TEMPLATE+"/single.html"
#saving memcache
        render = template.render(path, template_values)
        
        if wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+self.request.path,render)
        self.response.out.write(render)
        
class TagsAndCats(webapp.RequestHandler):
    def get(self):
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.out.write(data)
            return 
        page=1
        info = self.request.path.split("/")
        if len(info)==5:
            page=int(info[4])
        if info[1]=="tag":
            ar = WPArticles.getArticlesByTag(info[2],wpfe.NB_ARTICLE_HOME,(page-1)*wpfe.NB_ARTICLE_HOME)
        elif info[1]=="category":
            ar = WPArticles.getArticlesByCat(info[2],wpfe.NB_ARTICLE_HOME,(page-1)*wpfe.NB_ARTICLE_HOME)
        if len(ar)==0:
            return 404
        template_values = {
           'articles': ar,
           'title':info[2],
           'ParentTmpl': wpfe.TEMPLATE+"/index.html",
           'archive':True,
           'home':True,
           'blog_name':wpfe.BLOG_NAME,
           'blog_descr':wpfe.BLOG_DESCR,
           'blog_feed':wpfe.BLOG_FEED,
           'blog_about':wpfe.BLOG_ABOUT,
           'archives': WPArticles.getArticles(5,0),
           'twitter':wpfe.TWITTER_LOGIN,
           'categories':WPCategory.getCategories(),
           'page':page,
           'nxtPage': (int(page)+1),
           'prvPage': (int(page)-1),
           'nbArticles':len(ar),
           'urlArchive':"/"+info[1]+"/"+info[2]
        }
        path = wpfe.TEMPLATE+"/home.html"
#saving memcache
        render = template.render(path, template_values)
        if wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+self.request.path,render)
        self.response.out.write(render)
        
class Feed(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        self.response.out.write(RSS.getFeedUrl(wpfe.BLOG_URL+self.request.path))
        
class CDN(webapp.RequestHandler):
    def get(self):
        url = self.request.path
        media = CDNMedia.getMediaByUrl(wpfe.BLOG_URL+url)
        if not media:
            self.error(404)
            return
        self.response.headers["Content-Type"] = media.type
        self.response.headers["Expires"] = DateTime.getGmt()
        self.response.headers["Cache-Control"] = "max-age="+str(wpfe.CDN_CACHE_TIME)
        self.response.out.write(media.content)