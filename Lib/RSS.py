from Models.RSS import RSSContent
from google.appengine.api import urlfetch
import wpfe
import datetime

def getFeedUrl(url):
    t = RSSContent.all().filter("url", url).order("-date").fetch(1, 0)
    if t :
        t = t[0]
        if t.date+datetime.timedelta(minutes=wpfe.FEED_REFRESH) > datetime.datetime.today():#si ca date de moins d'un jour on prend de la base sinon, ...
            return t.content
    t = urlfetch.Fetch(url=url).content
    feed = RSSContent()
    feed.content=t
    feed.url=url
    feed.put()
    return t