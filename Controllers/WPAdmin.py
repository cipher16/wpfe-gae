from google.appengine.ext import webapp
from xml.dom.minidom import parseString

from google.appengine.ext import db
from Models.WordPress import *
from Lib.DateTime import date

class WPAdmin(webapp.RequestHandler):
    def get(self):
        self.response.out.write("")

class WPUploader(webapp.RequestHandler):
    def get(self):
        self.response.out.write("Upload de fichiers<form method='post' enctype=\"multipart/form-data\" action=\"/admin/upload\"><input type=\"file\" name=\"myfile\" /><input type=\"submit\" /></form>")

    def post(self):
        file_contents = self.request.get('myfile')
        if len(file_contents)==0:
            self.redirect("/admin/upload")
            return
        start = 0
        end   = 1000000 #Google's characters limitation
        Filen = len(file_contents)
        if Filen<end:
            self.response.out.write("le fichier fait moins de 1Mo on stock direct")
            upload = BlogUpload()
            upload.content = file_contents
            upload.num = Filen
            upload.put()
        else:
            nextBreak=False
            while True:
                oneMoContent = file_contents[start:end]
                upload = BlogUpload()
                upload.content = oneMoContent
                upload.num = Filen
                upload.put()
                start = end
                end *=2
                self.response.out.write("une boucle ...<br />");
                if nextBreak:
                    break
                if end>Filen:
                    end=Filen
                    nextBreak=True
            self.response.out.write("le fichier fait plus de 1 Mo, on explode en partie de 1Mo")
        #    self.redirect("/admin/import")#send to import part once we have stored data
        #    return
        #while(True):
        #    cutFile = file_contents[start:end]
        

class WPImporter(webapp.RequestHandler):
    def get(self):
        self.response.out.write("Choose your last upload to import in DB :<br />")
        lastNum = 0
        for i in db.GqlQuery("SELECT * FROM BlogUpload").fetch(100):
            if lastNum != i.num:
                lastNum=i.num
                self.response.out.write("<form method='post'><input name='lastImport' type='hidden' value='"+str(i.num)+"' />Upload du : "+str(i.date)+" ("+str(i.num)+" octets)<input type='submit' /></form>")
                
    def post(self):
        #as the file is may be to big to be stored, we start processing :s
        file_contents = ""
        dataToChoose = self.request.get('lastImport')
        data = db.GqlQuery("SELECT * FROM BlogUpload WHERE num = :1",int(dataToChoose)).fetch(100)
        for d in data:
            file_contents+=d.content
        if len(file_contents)==0:
            self.redirect("/admin/import")
            return
        dom = parseString(file_contents.decode('utf-8','replace').encode('utf-8',"replace"))
        
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
            type = cat.getElementsByTagName('wp:post_type')[0].childNodes[0].nodeValue
            #recuperation des categories et tags
            tags = []
            cats = []
            for t in cat.getElementsByTagName('category'):
                if "domain" in t.attributes.keys() and t.attributes["domain"].value=="tag" and "nicename" in t.attributes.keys() :
                    if not t.attributes["nicename"].value in tags:
                        tags.append(t.attributes["nicename"].value)
                elif "nicename" in t.attributes.keys():
                    #tag.append(t.childNodes[0].nodeValue)
                    if not t.attributes["nicename"].value in cats:
                        cats.append(t.attributes["nicename"].value)
            if status=="publish":
                                
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
                    n.type = type
                    n.content = cont
                    n.tags = tags
                    n.cats = cats
                    n.put()
                    self.response.out.write("[POST] --- l'element : "+title+" n'existe pas<br />")
                    
                    #recuperations des commentaires, si le post existe !!
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
                                r = db.GqlQuery('SELECT * FROM BlogComments WHERE idP = :1', int(comId)).fetch(1)
                                if not r:
                                    nCom = BlogComments()
                                    nCom.idP = int(comId)
                                    nCom.date = date.StrToDateTime(comDa)
                                    nCom.author = comAu
                                    nCom.authorIp = comAI
                                    nCom.authorMail = comAe
                                    nCom.authorUrl = comAR
                                    nCom.content = comCn
                                    nCom.post = n.key()
                                    nCom.put()
                                    self.response.out.write("un nouveau commentaire "+comId+" de : "+comAu+"<br />")