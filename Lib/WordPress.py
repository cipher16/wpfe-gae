from google.appengine.ext import db

class WPArticles:
    @staticmethod
    def getArticles(num=10, start=0):
        return db.GqlQuery('SELECT * FROM BlogPost order by date DESC').fetch(num,start)
