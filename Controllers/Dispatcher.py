from google.appengine.ext import webapp
from Lib.WordPress import *
from google.appengine.ext.webapp import template
import wpfe
from google.appengine.api import memcache
from Lib import RSS, DateTime, reCaptcha
from Models.WordPress import BlogPost, BlogComments
from datetime import datetime

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
            memcache.add(wpfe.BLOG_URL+self.request.path,render,(wpfe.ART_CACHE_TIME*60))
        self.response.out.write(render)
            
class Dispatcher(webapp.RequestHandler):
    def get(self,comment=None,error=None):
        #memcache system
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data and wpfe.ENABLE_CACHE and comment is None:#si pas de commentaire on balance le cache sinon on recharge
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
        
        #antispam
        if error:
            rehtml = reCaptcha.displayhtml(wpfe.RECAPTCHA_PUBLIC,error=error)
        else:
            rehtml = reCaptcha.displayhtml(wpfe.RECAPTCHA_PUBLIC)
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
            'prevArticle':pr,
            'rehtml':rehtml
        }
        path = wpfe.TEMPLATE+"/single.html"
#saving memcache
        render = template.render(path, template_values)
        
        if wpfe.ENABLE_CACHE:
            memcache.set(wpfe.BLOG_URL+self.request.path,render,(wpfe.ART_CACHE_TIME*60))
        self.response.out.write(render)
    #reception de commentaire
    def post(self):
        challenge = self.request.get('recaptcha_challenge_field')
        response  = self.request.get('recaptcha_response_field')
        remoteip  = self.request.remote_addr
    
        cResponse = reCaptcha.submit(challenge,response,wpfe.RECAPTCHA_PRIVATE,remoteip)
    
        if cResponse.is_valid:
            #insertion du commentaire
            #et 'redirection'
            idP = self.request.get("comment_post_ID")
            post = WPArticles.getArticle(int(idP))
            if post:
                post=post[0]

                author = self.request.get("author")
                email = self.request.get("email")
                url = self.request.get("url")                   #not required
                comment = self.request.get("comment")
                if author != "" and email != "" and comment!="":
                    com = BlogComments()
                    com.content=comment
                    com.sync = 0
                    com.author = author                         #we will have to sync it later
                    com.authorUrl  = url
                    com.authorMail = email
                    com.authorIp   = self.request.remote_addr
                    com.post = post
                    com.date = datetime.now()
                    com.put()
            
            self.get(comment="ok")
        else:
            #on renvoi et on informe sur les erreurs
            error = cResponse.error_code
            self.get(comment="",error=error)
        
class TagsAndCats(webapp.RequestHandler):
    def get(self):
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.out.write(data)
            return 
        page=1

        info = self.request.path.split("/")
        indexToRetrieve=len(info)-1
        if "page" in info:
            page=int(info[len(info)-1])
            info.pop(-1)
            info.pop(-1)
            indexToRetrieve-=2
        logging.info("index : "+str(indexToRetrieve)+ " " + str(len(info))+" "+info[indexToRetrieve])
        urlArchive = "/".join(info)
        if info[1]=="tag":
            ar = WPArticles.getArticlesByTag(info[indexToRetrieve],wpfe.NB_ARTICLE_HOME,(page-1)*wpfe.NB_ARTICLE_HOME)
        elif info[1]=="category":
            ar = WPArticles.getArticlesByCat(info[indexToRetrieve],wpfe.NB_ARTICLE_HOME,(page-1)*wpfe.NB_ARTICLE_HOME)
        if len(ar)==0:
            self.error(404)
        #    return
        template_values = {
           'articles': ar,
           'title':info[indexToRetrieve],#xss ??
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
           'urlArchive':urlArchive
        }
        path = wpfe.TEMPLATE+"/home.html"
#saving memcache
        render = template.render(path, template_values)
        if wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+self.request.path,render,(wpfe.ART_CACHE_TIME*60))
        self.response.out.write(render)
        
class Feed(webapp.RequestHandler):
    def get(self):
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        self.response.headers["Content-Type"] = "text/xml"
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.out.write(data)
            return
        data = RSS.getFeedUrl(wpfe.BLOG_URL+self.request.path)
        if wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+self.request.path,data,(wpfe.FEED_REFRESH*60))
        self.response.out.write(data)
        
class CDN(webapp.RequestHandler):
    def get(self):
        data = memcache.get(wpfe.BLOG_URL+self.request.path)
        if data is not None and wpfe.ENABLE_CACHE:
            self.response.headers["Content-Type"] = data.type
            self.response.headers["Expires"] = DateTime.getGmt()
            self.response.headers["Cache-Control"] = "max-age="+str(wpfe.CDN_CACHE_TIME)
            self.response.out.write(data.content)
            return
        url = self.request.path
        media = CDNMedia.getMediaByUrl(wpfe.BLOG_URL+url)
        if not media:
            self.error(404)
            return
        if wpfe.ENABLE_CACHE:
            memcache.add(wpfe.BLOG_URL+url,media,(wpfe.CDN_CACHE_TIME*60))
        self.response.headers["Content-Type"] = media.type
        self.response.headers["Expires"] = DateTime.getGmt()
        self.response.headers["Cache-Control"] = "max-age="+str(wpfe.CDN_CACHE_TIME)
        self.response.out.write(media.content)