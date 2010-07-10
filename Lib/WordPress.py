from google.appengine.ext import db
import wpfe

def rewUrl(url):
    return url.replace(wpfe.BLOG_URL ,"")
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
            ar.link=rewUrl(ar.link)
            #ar.comments=WPComments.getComments(ar.idP)S
            ar.resume=readMore(ar.content,ar.link,ar.title)
        return articles
    @staticmethod
    def getNextArticles(id,num=1):
        return db.GqlQuery('SELECT * FROM BlogPost WHERE idP > :1 order by idP ASC',id).fetch(num)
    @staticmethod
    def getPrevArticles(id,num=1):
        return db.GqlQuery('SELECT * FROM BlogPost WHERE idP < :1 order by idP DESC',id).fetch(num)
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
        article.link=rewUrl(article.link)
        return article
    
#useless due to the use of referenceProperty
class WPComments:
    @staticmethod
    def getComments(postId,num=100):
        return db.GqlQuery('SELECT * FROM BlogComments WHERE post_id = :1 order by date ASC',postId).fetch(num)
    
class WPCategory:
    @staticmethod
    def getNiceName(cat):
        cat = db.GqlQuery('SELECT * FROM BlogCategory WHERE catName = :1',cat).fetch(1)
        if not cat:
            return None
        return cat[0].niceName    
    @staticmethod
    def genUrl(cats):
        url = []
        for cat in cats:
            url.append("<a href='/category/"+WPCategory.getNiceName(cat)+"'>"+cat+"</a>")
        return ",".join(url)

class WPTags:
    @staticmethod
    def getNiceName(tag):
        tag = db.GqlQuery('SELECT * FROM BlogTag WHERE name = :1',tag).fetch(1)
        if not tag:
            return None
        return tag[0].slug
    @staticmethod
    def genUrl(tags):
        url = []
        for tag in tags:
            url.append("<a href='/tag/"+WPTags.getNiceName(tag)+"'>"+tag+"</a>")
        return ",".join(url)