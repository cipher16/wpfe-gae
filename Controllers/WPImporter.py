from google.appengine.ext import webapp
from xml.dom.minidom import parseString

from google.appengine.ext import db
from Models.WordPress import *
from Lib.DateTime import date

class WPImporter(webapp.RequestHandler):
    def get(self):
        self.response.out.write("Upload de fichiers<form method='post' enctype=\"multipart/form-data\" action=\"/admin/import\"><input type=\"file\" name=\"myfile\" /><input type=\"submit\" /></form>")
    def post(self):
        #as the file is may be to big to be stored, we start processing :s
        file_contents = self.request.get('myfile')
        if len(file_contents)==0:
            self.redirect("/")
            return
        dom = parseString(file_contents)
        
        title = dom.getElementsByTagName('channel')[0].getElementsByTagName('title')[0].childNodes[0].nodeValue
        link  = dom.getElementsByTagName('channel')[0].getElementsByTagName('link')[0].childNodes[0].nodeValue
        descr = dom.getElementsByTagName('channel')[0].getElementsByTagName('description')[0].childNodes[0].nodeValue
        pubDa = dom.getElementsByTagName('channel')[0].getElementsByTagName('pubDate')[0].childNodes[0].nodeValue
        lang  = dom.getElementsByTagName('channel')[0].getElementsByTagName('language')[0].childNodes[0].nodeValue
        
        #affichage d'infos de base juste pour test
        self.response.out.write("Blog title : "+title+" ("+link+")<br />"+descr)
        
        #importation des tags
        for cat in dom.getElementsByTagName('channel')[0].getElementsByTagName('wp:tag'):
            slug = cat.getElementsByTagName('wp:tag_slug')[0].childNodes[0].nodeValue
            name = cat.getElementsByTagName('wp:tag_name')[0].childNodes[0].nodeValue
            r = db.GqlQuery('SELECT * FROM BlogTag WHERE name = :1', name).fetch(1)
            if not r:
                n = BlogTag()
                n.name = name
                n.slug = slug
                n.put()
                self.response.out.write("[TAG] --- l'element : "+name+" n'existe pas<br />")
                
        #importation des categories
        for cat in dom.getElementsByTagName('channel')[0].getElementsByTagName('wp:category'):
            nice = cat.getElementsByTagName('wp:category_nicename')[0].childNodes[0].nodeValue
            name = cat.getElementsByTagName('wp:cat_name')[0].childNodes[0].nodeValue
            r = db.GqlQuery('SELECT * FROM BlogCategory WHERE catName = :1', name).fetch(1)
            if not r:
                n = BlogCategory()
                n.niceName = nice
                n.catName = name
                n.put()
                self.response.out.write("[CAT] --- l'element : "+name+" n'existe pas<br />")
        
        #importation des articles
        for cat in dom.getElementsByTagName('channel')[0].getElementsByTagName('item'):
            id =     cat.getElementsByTagName('wp:post_id')[0].childNodes[0].nodeValue
            Postdate =   cat.getElementsByTagName('wp:post_date')[0].childNodes[0].nodeValue
            status = cat.getElementsByTagName('wp:status')[0].childNodes[0].nodeValue
            title = cat.getElementsByTagName('title')[0].childNodes[0].nodeValue
            link = cat.getElementsByTagName('link')[0].childNodes[0].nodeValue
            author = cat.getElementsByTagName('dc:creator')[0].childNodes[0].nodeValue
                
            if status=="publish":
                
                #recuperations des commentaires, si il y a lieux
                if len(cat.getElementsByTagName('wp:comment'))>0:
                    for com in cat.getElementsByTagName('wp:comment'):
                        #verification si le commentaire est approuve
                        if com.getElementsByTagName("wp:comment_approved")[0].childNodes[0].nodeValue=="1":
                            comAR = ""
                            comAe = ""
                            comDa = com.getElementsByTagName("wp:comment_date")[0].childNodes[0].nodeValue
                            comId = com.getElementsByTagName("wp:comment_id")[0].childNodes[0].nodeValue
                            comAu = com.getElementsByTagName("wp:comment_author")[0].childNodes[0].wholeText
                            if len(com.getElementsByTagName("wp:comment_author_email")[0].childNodes)>0:
                                comAe = com.getElementsByTagName("wp:comment_author_email")[0].childNodes[0].nodeValue
                            if len(com.getElementsByTagName("wp:comment_author_url")[0].childNodes)>0:
                                comAR = com.getElementsByTagName("wp:comment_author_url")[0].childNodes[0].nodeValue
                            comAI = com.getElementsByTagName("wp:comment_author_IP")[0].childNodes[0].nodeValue
                            comCn = com.getElementsByTagName("wp:comment_content")[0].childNodes[0].wholeText
                            comPi = id
                            r = db.GqlQuery('SELECT * FROM BlogComments WHERE idP = :1', int(id)).fetch(1)
                            if not r:
                                nCom = BlogComments()
                                nCom.idP = int(comId)
                                nCom.date = date.StrToDateTime(comDa)
                                nCom.author = comAu
                                nCom.authorIp = comAI
                                nCom.authorMail = comAe
                                nCom.authorUrl = comAR
                                nCom.content = comCn
                                nCom.post_id = int(comPi)
                                nCom.put()
                                self.response.out.write("un nouveau commentaire "+comId+" de : "+comAu+"<br />")
                
                #recuperation du texte et test sur le contenu        
                cont = ""
                try:
                    cont = cat.getElementsByTagName('content:encoded')[0].childNodes[0].wholeText
                except IndexError:
                    self.response.out.write(id+" has a empty content<br />\n")
                r = db.GqlQuery('SELECT * FROM BlogPost WHERE idP = :1', int(id)).fetch(1)
                
                if not r and cont!="":
                    n = BlogPost()
                    n.idP = int(id)
                    n.date = date.StrToDateTime(Postdate)
                    n.title = title
                    n.author = author
                    n.status = status
                    n.link = link
                    n.content = cont
                    n.put()
                    self.response.out.write("[POST] --- l'element : "+title+" n'existe pas<br />")