from google.appengine.ext import db

class RSSContent(db.Model):
    content = db.BlobProperty()
    url = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)