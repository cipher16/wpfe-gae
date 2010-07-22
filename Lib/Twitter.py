import re
from google.appengine.api import urlfetch
from xml.dom.minidom import parseString
from google.appengine.api import memcache
import wpfe

def getLastTweet(user):
    tab = memcache.get("twitter_"+user)
    if tab is not None :
        return tab
    tab = {}
    xml = urlfetch.fetch("http://api.twitter.com/1/users/show/"+user+".xml").content
    dom = parseString(xml)
    tab['text']=dom.getElementsByTagName('user')[0].getElementsByTagName('status')[0].getElementsByTagName('text')[0].childNodes[0].nodeValue
    tab['source']=dom.getElementsByTagName('user')[0].getElementsByTagName('status')[0].getElementsByTagName('source')[0].childNodes[0].nodeValue
    tab['created_at']=dom.getElementsByTagName('user')[0].getElementsByTagName('status')[0].getElementsByTagName('created_at')[0].childNodes[0].nodeValue
#    for elem in dom.getElementsByTagName('user')[0].getElementsByTagName('status')[0].childNodes : #[0].getElementsByTagName('text')[0].childNodes[0].wholeText
#        if len(elem.childNodes)>0:
#python sux ... incapable de faire un truc aussi simple !!
#            tab[str(elem.nodeName)]=elem.childNodes[0].nodeValue
    tab = memcache.add("twitter_"+user,tab,(wpfe.TWITTER_CACHE*60))
    return tab