from Lib import WPXMLRPC
import wpfe
from google.appengine.ext import db
from Models.WordPress import BlogPost, BlogCategory, BlogTag, BlogComments,\
    BlogUser
from Lib.WordPress import WPCategory, WPTags, WPUser
import logging

#look back 5 post query db and update
def syncPost(nbPost):
    try:
        wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
        wp.selectBlog(0)#TODO: get the good blog
        #print wp.getLastPost().title.__str__()
        nbUp=0
        nbDown = 0
        for p in wp.getRecentPosts(nbPost):
            nbDown+=1
            d = db.GqlQuery("SELECT * FROM BlogPost WHERE idP = :1",p.id).fetch(1)
            user = WPUser.getUserById(p.user)
            if not d and p.status=="publish" and user is not None:
                nbUp+=1
                post = BlogPost()
                post.idP = p.id
                post.title = p.title
                post.content = p.content.replace(wpfe.BLOG_URL,"")
                post.author = user
                post.date = p.date
                post.link = p.link.replace(wpfe.BLOG_URL,"")
                post.status = p.status
                post.type = "post"
                for cat in p.categories:#overcrade!!!!
                    if cat is not None:
                        post.cats.append(WPCategory.getSlug(cat))
                for tag in p.tags.split(", "):#overcrade!!!!
                    tag=WPTags.getSlug(tag)
                    if tag is not None:
                        post.tags.append(tag)
                post.put()
        return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)
    except Exception,fault:
        return "Une erreur est survenue : "+fault.__str__()

def syncTags():
    try:
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
    except Exception,fault:
        return "Une erreur est survenue : "+fault.__str__()

def syncComments():
    try:
        wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
        wp.selectBlog(0)#TODO: get the good blog
        #print wp.getLastPost().title.__str__()
        nbUp=0
        nbDown = 0
#can't do it using this way ...too many HTTP request
#        d = db.GqlQuery("SELECT * FROM BlogPost").fetch(1000)#get last 1000 articles
#        for bp in d:
#            logging.info("Selecting POST : "+str(bp.idP))
#            for p in wp.getCommentList(bp.idP,200):#get last 200 comments per articles so ...
#                nbDown+=1
#                logging.info("Selecting Comment : "+str(p.id))
#                d = db.GqlQuery("SELECT * FROM BlogComments WHERE idP = :1",int(p.id)).fetch(1)
#                if not d:
        for p in wp.getCommentList(None,2000):#retrieve last 2000 comments ...
            nbDown+=1
            d = db.GqlQuery("SELECT * FROM BlogComments WHERE idP = :1",int(p.id)).fetch(1)
            if not d:
                logging.info("Getting"+p.post_id)
                bp = db.GqlQuery("SELECT * FROM BlogPost WHERE idP = :1",int(p.post_id)).fetch(1)
                if bp is not None:#si le post existe
                    bp=bp[0]
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
    except Exception,fault:
        return "Une erreur est survenue : "+fault.__str__()
#unusable because WP made shit with his RPC services ... no slug
def syncCats():
    try:
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
    except Exception,fault:
        return "Une erreur est survenue : "+fault.__str__()
def syncUsers():
    try:
        wp=WPXMLRPC.WordPressClient(wpfe.RPC_URL, wpfe.RPC_LOGIN, wpfe.RPC_PASSW)
        wp.selectBlog(0)#TODO: get the good blog
        #print wp.getLastPost().title.__str__()
        nbUp=0
        nbDown = 0
        for p in wp.getAuthors():
            nbDown+=1
            d = db.GqlQuery("SELECT * FROM BlogUser WHERE uId = :1",int(p.id)).fetch(1)
            if not d:
                nbUp+=1
                cat = BlogUser()
                cat.name = p.name
                cat.uId = int(p.id)
                cat.put()
        return "Synchronisation de "+str(nbUp)+" sur "+str(nbDown)
    except Exception,fault:
       return "Une erreur est survenue : "+fault.__str__()
def syncAll():
    syncUsers()
    syncCats()
    syncTags()
    syncPost(100000)
    syncComments()