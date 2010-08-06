from Models.RSS import RSSContent
from google.appengine.api import urlfetch, memcache
import wpfe
import datetime

def getFeedUrl(url):
    t = memcache.get("feed_"+url)
    content = ""
    if t is not None :
        return t
    t = RSSContent.all().filter("url", url).order("-date").fetch(1, 0)
    if t :
        t = t[0]
        if t.date+datetime.timedelta(minutes=wpfe.FEED_REFRESH) > datetime.datetime.today():#si ca date de moins d'un jour on prend de la base sinon, ...
            return t.content
        content = t.content
    try:
        t = urlfetch.Fetch(url=url).content
        feed = RSSContent()
        feed.content=t.replace(wpfe.BLOG_URL,"")#delete origin
        feed.url=url
        feed.put()
        memcache.add("feed_"+url,feed.content,(wpfe.FEED_REFRESH*60))
        return feed.content
    except Exception:
        if content !="": #in case we can't retrieve feed, provide old one
            return content
        return None