from google.appengine.ext import webapp
from Lib.WordPress import WPArticles
from google.appengine.ext.webapp import template
import wpfe

class Home(webapp.RequestHandler):
    def get(self):
        ar = WPArticles.getArticles(10)
        template_values = {
           'articles': ar,
           'headerTemp':wpfe.TEMPLATE+"/header.html"
        }
        path = wpfe.TEMPLATE+"/home.html"
        self.response.out.write(template.render(path, template_values))

        #self.response.out.write('HOME'+path)

class Dispatcher(webapp.RequestHandler):
    def get(self):
        self.response.out.write('ok'+self.request.path)