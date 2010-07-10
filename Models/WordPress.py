from google.appengine.ext import db

class BlogPost(db.Model):
    idP = db.IntegerProperty()
    date = db.DateTimeProperty()
    title = db.StringProperty()
    author= db.StringProperty()
    status= db.StringProperty()
    link  = db.StringProperty()
    type  = db.StringProperty()
    content=db.TextProperty()
    tags = db.StringListProperty()
    cats = db.StringListProperty()

class BlogComments(db.Model):
    idP = db.IntegerProperty()
    author = db.StringProperty()
    authorUrl = db.StringProperty()
    authorMail = db.StringProperty()
    authorIp = db.StringProperty()
    date = db.DateTimeProperty()
    content = db.TextProperty()
    post = db.ReferenceProperty(BlogPost,collection_name="comments")#BlogPost

class BlogCategory(db.Model):
    niceName = db.StringProperty()
    catName = db.StringProperty()

class BlogTag(db.Model):
    slug = db.StringProperty()
    name = db.StringProperty()