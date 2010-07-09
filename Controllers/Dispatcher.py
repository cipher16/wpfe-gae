from google.appengine.ext import webapp
from Lib.WordPress import WPArticles
from google.appengine.ext.webapp import template
import wpfe

#type : 
#    home (display 10)
#    single (display 1)
#    page (display a page)

class Home(webapp.RequestHandler):
    def get(self):
        page=0
        if self.request.path.startswith("/page/"):
            page=self.request.path.split("/")
            if len(page)<3:
                page=0
            else:
                page=int(page[2])
            
        ar = WPArticles.getArticles(10,page*10)
        template_values = {
           'articles': ar,
           'ParentTmpl': wpfe.TEMPLATE+"/index.html",
           'home':True,
           'blog_name':wpfe.BLOG_NAME,
           'blog_descr':wpfe.BLOG_DESCR,
           'blog_feed':wpfe.BLOG_FEED,
           'page':page,
           'nxtPage': (int(page)+1),
           'prvPage': (int(page)-1)
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