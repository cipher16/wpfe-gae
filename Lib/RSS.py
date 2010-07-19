from Models.RSS import RSSContent
from google.appengine.api import urlfetch

def getFeedUrl(url):
    t = RSSContent.all().filter("url", url).order("-date").fetch(1, 0)
    if t :
        return t[0].content
    t = urlfetch.Fetch(url=url).content
    feed = RSSContent()
    feed.content=t
    feed.url=url
    feed.put()
    return t