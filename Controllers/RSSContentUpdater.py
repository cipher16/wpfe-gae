from google.appengine.ext import webapp
from Models.RSS import RSSContent
from xml.dom.minidom import parse, parseString
from google.appengine.api import urlfetch
from google.appengine.ext import db
import wpfe

class RssContentUpdater(webapp.RequestHandler):        
    def get(self):
        url = wpfe.BLOG_FEED
        xml = ""
        #recuperation de l'url
        results = db.GqlQuery("SELECT * FROM RSSContent WHERE url = :1", url).fetch(1)
        if not results:
            #url du site
            xml = urlfetch.fetch(url).content
            
            rsscontent = RSSContent()
            rsscontent.content=unicode(xml,'utf-8',errors='replace')    
            rsscontent.url=url
            rsscontent.put()
            
        else:
            xml = results[0].content
        #parsing du document
        dom = parseString(xml)
        
        #data
        title = dom.getElementsByTagName('channel')[0].getElementsByTagName('title')[0].childNodes[0].nodeValue
        link  = dom.getElementsByTagName('channel')[0].getElementsByTagName('link')[0].childNodes[0].nodeValue
        descr = dom.getElementsByTagName('channel')[0].getElementsByTagName('description')[0].childNodes[0].nodeValue
        pubDa = dom.getElementsByTagName('channel')[0].getElementsByTagName('pubDate')[0].childNodes[0].nodeValue
        lang  = dom.getElementsByTagName('channel')[0].getElementsByTagName('language')[0].childNodes[0].nodeValue
        
        self.response.out.write(title+" "+link+" "+descr+" "+pubDa+" "+lang+"<br />")

        #parsing category
        for cat in dom.getElementsByTagName('channel')[0].getElementsByTagName('category'):
            self.response.out.write("Nom : "+cat.childNodes[0].nodeValue+"<br />")
        
        #parsing category
        for cat in dom.getElementsByTagName('channel')[0].getElementsByTagName('tag'):
            self.response.out.write("Nom : "+cat.childNodes[0].nodeValue+"<br />")