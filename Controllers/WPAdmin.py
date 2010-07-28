from google.appengine.ext import webapp
from xml.dom.minidom import parseString
from google.appengine.ext.webapp import template
import wpfe
from google.appengine.ext import db
from Models.WordPress import *
from google.appengine.api.labs.taskqueue import taskqueue
import Models
from google.appengine.api import memcache
from Lib import DateTime, WPXMLRPC, UpdateRPC
import logging

class WPAdmin(webapp.RequestHandler):
    def get(self):
        path=""
        valu={}
        if self.request.get("page")=="nettoyage":
            path = wpfe.TEMPLATE+"/admin/nettoyage.html"
            valu = self.nettoyage(self.request.get("del"))
        elif self.request.get("page")=="cache":
            path = wpfe.TEMPLATE+"/admin/cache.html"
            valu = self.cache(self.request.get("flush"))     
        elif self.request.get("page")=="rpcupdate":
            path = wpfe.TEMPLATE+"/admin/rpc.html"
            valu = self.rpc(self.request.get("par"))            
        else:
            path = wpfe.TEMPLATE+"/admin/admin.html"
        self.response.out.write(template.render(path,valu))
    def cache(self,f=""):
        mem = memcache
        if f!="":
            mem.flush_all()
        return {
              'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html",
              'cacheInfo': mem.get_stats()
        }
    def nettoyage(self,d=""):
        if d=="tag":
            db.delete(Models.WordPress.BlogTag.all())
        elif d=="com" :
            db.delete(Models.WordPress.BlogComments.all())
        elif d=="art" :
            db.delete(Models.WordPress.BlogPost.all())
        elif d=="cat" :
            db.delete(Models.WordPress.BlogCategory.all())
            
        return {
                'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html",
                'tags':Models.WordPress.BlogTag.all().fetch(10),
                'categories':Models.WordPress.BlogCategory.all().fetch(10),
                'articles':Models.WordPress.BlogPost.all().order('-date').fetch(10),
                'commentaires':Models.WordPress.BlogComments.all().order('-date').fetch(10)
        }
    def rpc(self,par):
        text=""
        if par=="syncpost":
            text=UpdateRPC.syncPost(5)
        elif par=="synccats":
            text=UpdateRPC.syncCats()
        elif par=="synctags":
            text=UpdateRPC.syncTags()
        elif par=="synccoms":
            text=UpdateRPC.syncComments()
        elif par=="syncusers":
            text=UpdateRPC.syncUsers()
        elif par=="syncall":
            taskqueue.add(url='/admin/?page=rpcupdate&par=syncrpcall',method="GET")
            text="L'ajout de votre requete a ete mise en 'task queue' et prendra un peu de temps, merci de patienter"
            #UpdateRPC.syncUsers()
        elif par=="syncrpcall":
            logging.info("Mise a jour via rpc en cours")
            UpdateRPC.syncAll()
            logging.info("Mise a jour via rpc termine")
        return {'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html","texte":text}

class WPUploader(webapp.RequestHandler):
    def get(self):
        path = wpfe.TEMPLATE+"/admin/upload.html"
        self.response.out.write(template.render(path,{'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html"}))

    def post(self):
        file_contents = self.request.get('myfile')
        info = {
            'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html",
            'Import':True
        }
        if len(file_contents)==0:
            self.redirect("/admin/upload")
            return
        incre = 1000000
        start = 0
        end   = incre #Google's characters limitation
        Filen = len(file_contents)
        if Filen<end:
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
                end +=incre
                if nextBreak:
                    break
                if end>Filen:
                    end=Filen
                    nextBreak=True
        self.redirect("/admin/import")

class WPImporter(webapp.RequestHandler):
    def get(self):
        lastNum = 0
        suppression = False
        contenu = ""
        upload = []
        if self.request.get('deleteContent'):
            d = db.GqlQuery("SELECT * FROM BlogUpload WHERE num=:1",int(self.request.get('num'))).fetch(100)
            db.delete(d)
            suppression=True
        if self.request.get('startTask'):
            taskqueue.add(url='/admin/import',params={'lastImport': self.request.get('num')})
        if self.request.get('displayContent'):
            for d in db.GqlQuery("SELECT * FROM BlogUpload WHERE num=:1",int(self.request.get('num'))).fetch(100):
                contenu+=d.content
        else:
            for i in db.GqlQuery("SELECT * FROM BlogUpload").fetch(100):
                if lastNum != i.num:
                    lastNum=i.num
                    upload.append(i)
        path = wpfe.TEMPLATE+"/admin/import.html"
        self.response.out.write(template.render(path,
            {
                'ParentTmpl': wpfe.TEMPLATE+"/admin/admin.html",
                'xmlContent': contenu,
                'suppress':suppression,
                'upload': upload
            })
        )       

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
            link = cat.getElementsByTagName('link')[0].childNodes[0].nodeValue.replace(wpfe.BLOG_URL,"")
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
                    cont = cat.getElementsByTagName('content:encoded')[0].childNodes[0].wholeText.replace(wpfe.BLOG_URL,"").replace("<pre ","<pre class='prettyprint' ")
                except IndexError:
                    self.response.out.write(id+" has an empty content<br />\n")
                r = db.GqlQuery('SELECT * FROM BlogPost WHERE idP = :1', int(id)).fetch(1)
                
                if not r and cont!="":
                    n = BlogPost()
                    n.idP = int(id)
                    n.date = DateTime.StrToDateTime(Postdate)
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
                                    nCom.date = DateTime.StrToDateTime(comDa)
                                    nCom.author = comAu
                                    nCom.authorIp = comAI
                                    nCom.authorMail = comAe
                                    nCom.authorUrl = comAR
                                    nCom.content = comCn
                                    nCom.post = n.key()
                                    nCom.put()
                                    self.response.out.write("un nouveau commentaire "+comId+" de : "+comAu+"<br />")