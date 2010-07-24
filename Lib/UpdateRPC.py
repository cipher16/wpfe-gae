from Lib import WPXMLRPC
import wpfe
from google.appengine.ext import db
from Models.WordPress import BlogPost, BlogCategory, BlogTag, BlogComments
from Lib.WordPress import WPCategory, WPTags

#look back 5 post query db and update
def syncPost(nbPost=5):
    wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
    wp.selectBlog(0)#TODO: get the good blog
    #print wp.getLastPost().title.__str__()
    nbUp=0
    nbDown = 0
    for p in wp.getRecentPosts(nbPost):
        nbDown+=1
        d = db.GqlQuery("SELECT * FROM BlogPost WHERE idP = :1",p.id).fetch(1)
        if not d:
            nbUp+=1
            post = BlogPost()
            post.idP = p.id
            post.title = p.title
            post.content = p.description
            post.author = p.user
            post.date = p.date
            post.link = p.link
            post.type = "post"
            for cat in p.categories:#overcrade!!!!
                post.cats.append(WPCategory.getSlug(cat))
            for tag in p.tags.split(", "):#overcrade!!!!
                post.tags.append(WPTags.getSlug(tag))
            post.put()
    return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)

def syncTags():
    wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
    wp.selectBlog(0)#TODO: get the good blog
    #print wp.getLastPost().title.__str__()
    nbUp=0
    nbDown = 0
    for p in wp.getTagList():
        nbDown+=1
        d = db.GqlQuery("SELECT * FROM BlogTag WHERE slug = :1",p.slug).fetch(1)
        if not d:
            nbUp+=1
            t = BlogTag()
            t.slug = p.slug
            t.name = p.name
            t.put()
    return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)

def syncComments():
    wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
    wp.selectBlog(0)#TODO: get the good blog
    #print wp.getLastPost().title.__str__()
    nbUp=0
    nbDown = 0
    d = db.GqlQuery("SELECT * FROM BlogPost").fetch(1000)
    for bp in d:
        for p in wp.getCommentList(bp.idP):
            nbDown+=1
            d = db.GqlQuery("SELECT * FROM BlogComments WHERE idP = :1",p.id).fetch(1)
            if not d:
                nbUp+=1
                t = BlogComments()
                t.sync = 1
                t.idP = p.id
                t.authorIp = p.au_ip
                t.authorMail = p.au_mail
                t.authorUrl = p.au_url
                t.author = p.author
                t.content = p.content
                t.post = bp
                t.date = p.date
                t.put()
    return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)
#unusable because WP made shit with his RPC services ... no slug
def syncCats():
    wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
    wp.selectBlog(0)#TODO: get the good blog
    #print wp.getLastPost().title.__str__()
    nbUp=0
    nbDown = 0
    for p in wp.getCategoryList():
        nbDown+=1
        d = db.GqlQuery("SELECT * FROM BlogCategory WHERE catName = :1",p.name).fetch(1)
        if not d:
            nbUp+=1
            cat = BlogCategory()
            cat.catName = p.name
            cat.catId = p.id
            cat.catParentId = p.pid
            cat.niceName = p.niceName
            cat.put()
    return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)