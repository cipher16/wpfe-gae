from google.appengine.ext import db
from google.appengine.api import urlfetch
from Models import WordPress
import logging
from Models.WordPress import BlogUser

def readMore(content,url,title):
    if content.find("<!--more-->")==-1:
        return content
    r=content.split("<!--more-->")
    return "<p>"+r[0]+"</p><p><a href='"+url+"' class='more-link'>Lire la suite : "+title+"</a></p>"

class WPArticles:
    @staticmethod
    def getArticles(num=10, start=0):
        articles = db.GqlQuery('SELECT * FROM BlogPost WHERE type=:1 order by date DESC',"post").fetch(num,start)
        for ar in articles:
            #ar.comments=WPComments.getComments(ar.idP)S
            ar.resume=readMore(ar.content,ar.link,ar.title)
            ar.category=WPCategory.genUrl(ar.cats)
            ar.tagsURL=WPTags.genUrl(ar.tags)
        return articles
    @staticmethod
    def getNextArticles(id,num=1):
        return db.GqlQuery('SELECT * FROM BlogPost WHERE idP > :1 AND type=:2 order by idP ASC',id,"post").fetch(num)
    @staticmethod
    def getPrevArticles(id,num=1):
        return db.GqlQuery('SELECT * FROM BlogPost WHERE idP < :1 AND type=:2 order by idP DESC',id,"post").fetch(num)
    @staticmethod
    def getArticle(id):
        article = db.GqlQuery('SELECT * FROM BlogPost WHERE idP = :1',id).fetch(1)
        return article
    @staticmethod
    def getArticleByUrl(link):
        article = db.GqlQuery('SELECT * FROM BlogPost WHERE link = :1',link).fetch(1)
        if len(article)==0:
            return None
        article = article[0]
        #article.comments = WPComments.getComments(article.idP)
        article.coms=article.comments.order('date')
        return article
    @staticmethod
    def getArticlesByTag(tag,num=10,start=0):
        articles = db.GqlQuery('SELECT * FROM BlogPost WHERE tags = :1 AND type=:2 order by date DESC',tag,"post").fetch(num,start)
        for ar in articles:
            #ar.comments=WPComments.getComments(ar.idP)S
            ar.resume=readMore(ar.content,ar.link,ar.title)
            ar.category=WPCategory.genUrl(ar.cats)
            ar.tagsURL=WPTags.genUrl(ar.tags)
        return articles
    @staticmethod
    def getArticlesByCat(cat,num=10,start=0):
        articles = db.GqlQuery('SELECT * FROM BlogPost WHERE cats = :1 AND type=:2 order by date DESC',cat,"post").fetch(num,start)
        for ar in articles:
            #ar.comments=WPComments.getComments(ar.idP)S
            ar.resume=readMore(ar.content,ar.link,ar.title)
            ar.category=WPCategory.genUrl(ar.cats)
            ar.tagsURL=WPTags.genUrl(ar.tags)
        return articles
    
    
#useless due to the use of referenceProperty
class WPComments:
    @staticmethod
    def getComments(postId,num=100):
        return db.GqlQuery('SELECT * FROM BlogComments WHERE post_id = :1 order by date ASC',postId).fetch(num)
    
class WPCategory:
    @staticmethod
    def getName(cat):
        cat = db.GqlQuery('SELECT * FROM BlogCategory WHERE niceName = :1',cat).fetch(1)
        if not cat:
            return None
        return cat[0].catName    
    @staticmethod
    def getSlug(cat):
        cat = db.GqlQuery('SELECT * FROM BlogCategory WHERE catName = :1',cat).fetch(1)
        if not cat:
            return None
        return cat[0].niceName
    @staticmethod
    def genUrl(cats):
        url = []
        for cat in cats:
            url.append("<a href='/category/"+WPCategory.genUrlParent(cat)+cat+"'>"+WPCategory.getName(cat)+"</a>")
        return ",".join(url)
    @staticmethod
    def genUrlParent(cat):
        url=""
        d = db.GqlQuery("SELECT * FROM BlogCategory WHERE niceName=:1",cat).fetch(1)
        if not d:
            return url
        d=d[0]
        parent = d.catParentId
        while parent != 0:
            p = db.GqlQuery("SELECT * FROM BlogCategory WHERE catId=:1",parent).fetch(1)
            if not p:
                return url
            p = p[0]
            url=p.niceName+"/"+url
            parent=p.catParentId
        return url
    @staticmethod
    def getCategories():
        d = db.GqlQuery("SELECT * FROM BlogCategory ORDER BY niceName").fetch(1000)
        cats = []
        if d:
            for c in d:
                c.parentUrl= WPCategory.genUrlParent(c.niceName)
                cats.append(c)
        return cats
        #return WordPress.BlogCategory().all().order('niceName')

class WPTags:
    @staticmethod
    def getName(tag):
        tag = db.GqlQuery('SELECT * FROM BlogTag WHERE slug = :1',tag).fetch(1)
        if not tag:
            return None
        return tag[0].name
    @staticmethod
    def getSlug(tag):
        tag = db.GqlQuery('SELECT * FROM BlogTag WHERE name = :1',tag).fetch(1)
        if not tag:
            return None
        return tag[0].slug
    @staticmethod
    def genUrl(tags):
        url = []
        for tag in tags:
            url.append("<a href='/tag/"+tag+"'>"+WPTags.getName(tag)+"</a>")
        return ",".join(url)
    
class WPUser:
    @staticmethod
    def getUserById(id):
        user = db.GqlQuery('SELECT * FROM BlogUser WHERE uId = :1',int(id)).fetch(1)
        if not user:
            return None
        return user[0].name

class CDNMedia:
    @staticmethod
    def getMediaByUrl(url):
        media = db.GqlQuery('SELECT * FROM CDNMedia WHERE url = :1',url).fetch(1)
        if not media:
            logging.info("Telechargement du fichier : "+url)
            media = WordPress.CDNMedia()
            #recuperation du media en ligne et insertion en base
            data = urlfetch.Fetch(url=url)
            if not data:
                return None
            media.content = data.content
            media.url = url
            if "Content-Type" in data.headers:
                media.type=data.headers["Content-Type"]
            media.put()
        else:
            media=media[0]
        return media