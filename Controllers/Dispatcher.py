from google.appengine.ext import webapp
from Lib.WordPress import *
from google.appengine.ext.webapp import template
import wpfe

#type : 
#    home (display 10)
#    single (display 1)
#    page (display a page)

class Home(webapp.RequestHandler):
    def get(self):
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
           'page':page,
           'nxtPage': (int(page)+1),
           'prvPage': (int(page)-1),
           'nbArticles':len(ar)
        }
        path = wpfe.TEMPLATE+"/home.html"
        self.response.out.write(template.render(path, template_values))
            
class Dispatcher(webapp.RequestHandler):
    def get(self):
        ar = WPArticles.getArticleByUrl(wpfe.BLOG_URL+self.request.path)        
        if not ar:
            self.response.out.write("404")
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
            'ParentTmpl': wpfe.TEMPLATE+"/index.html",
            'blog_name':wpfe.BLOG_NAME,
            'blog_descr':wpfe.BLOG_DESCR,
            'blog_feed':wpfe.BLOG_FEED,
            'single':True,
            'nextArticle':nx,
            'prevArticle':pr
        }
        path = wpfe.TEMPLATE+"/single.html"
        self.response.out.write(template.render(path, template_values))
        
class TagsAndCats(webapp.RequestHandler):
    def get(self):
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
           'ParentTmpl': wpfe.TEMPLATE+"/index.html",
           'archive':True,
           'home':True,
           'blog_name':wpfe.BLOG_NAME,
           'blog_descr':wpfe.BLOG_DESCR,
           'blog_feed':wpfe.BLOG_FEED,
           'page':page,
           'nxtPage': (int(page)+1),
           'prvPage': (int(page)-1),
           'nbArticles':len(ar),
           'urlArchive':"/"+info[1]+"/"+info[2]
        }
        path = wpfe.TEMPLATE+"/home.html"
        self.response.out.write(template.render(path, template_values))