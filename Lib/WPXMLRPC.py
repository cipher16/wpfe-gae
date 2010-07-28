"""
    wordpresslib.py
    
    WordPress xml-rpc client library
    use MovableType API
    
    Copyright (C) 2005 Michele Ferretti
    black.bird@tiscali.it
    http://www.blackbirdblog.it
    
    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA    02111-1307, USA.

    XML-RPC supported methods: 
        * getUsersBlogs
        * getUserInfo
        * getPost
        * getRecentPosts
        * newPost
        * editPost
        * deletePost
        * newMediaObject
        * getCategoryList
        * getTagsList
        * getPostCategories
        * setPostCategories
        * getTrackbackPings
        * publishPost
        * getPingbacks

    References:
        * http://codex.wordpress.org/XML-RPC_Support
        * http://www.sixapart.com/movabletype/docs/mtmanual_programmatic.html
        * http://docs.python.org/lib/module-xmlrpclib.html
"""
from django.template.defaultfilters import slugify

__author__ = "Michele Ferretti <black.bird@tiscali.it>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2005/05/02 $"
__copyright__ = "Copyright (c) 2005 Michele Ferretti"
__license__ = "LGPL"

import exceptions
import re
import os
import xmlrpclib
import datetime
import time

class WordPressException(exceptions.Exception):
    """Custom exception for WordPress client operations
    """
    def __init__(self, obj):
        if isinstance(obj, xmlrpclib.Fault):
            self.id = obj.faultCode
            self.message = obj.faultString
        else:
            self.id = 0
            self.message = obj

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.message)
        
class WordPressBlog:
    """Represents blog item
    """    
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False
        
class WordPressUser:
    """Represents user item
    """    
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.email = ''
        
class WordPressAuthors:
    """Represents authors item
    """    
    def __init__(self):
        self.id = ''
        self.login = ''
        self.name = ''

class WordPressCategory:
    """Represents category item
    """    
    def __init__(self):
        self.id = 0
        self.name = ''
        self.niceName = ''
        self.pid = ''
        self.isPrimary = False

class WordPressTag:
    """Represents tag item
    """    
    def __init__(self):
        self.id = 0
        self.name = ''
        self.slug = ''

class WordPressComments:
    def __init__(self):
        self.id=0
        self.status = ''
        self.content = ''
        self.link = ''
        self.post_id = ''
        self.author = ''
        self.au_mail = ''
        self.au_url = ''
        self.au_ip = ''

class WordPressPost:
    """Represents post item
    """    
    def __init__(self):
        self.id = 0
        self.title = ''
        self.date = None
        self.permaLink = ''
        self.description = ''
        self.textMore = ''
        self.excerpt = ''
        self.link = ''
        self.categories = []
        self.user = ''
        self.allowPings    = False
        self.allowComments = False

        
class WordPressClient:
    """Client for connect to WordPress XML-RPC interface
    """
    
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.blogId = 0
        self.categories = None
        self.comments = None
        self.tags = None
        self.authors = None
        self._server = xmlrpclib.ServerProxy(self.url)

    def _filterPost(self, post):
        """Transform post struct in WordPressPost instance 
        """
        postObj = WordPressPost()
        postObj.permaLink         = post['permaLink']
        postObj.description     = post['description']
        postObj.title             = post['title']
        postObj.excerpt         = post['mt_excerpt']
        postObj.user             = post['userid']
        postObj.date             = datetime.datetime.strptime(str(post['dateCreated']), "%Y%m%dT%H:%M:%S")
        postObj.link             = post['link']
        postObj.textMore         = post['mt_text_more']
        postObj.allowComments     = post['mt_allow_comments'] == 1
        postObj.id                 = int(post['postid'])
        postObj.categories         = post['categories']
        postObj.tags         = post['mt_keywords']
        postObj.allowPings         = post['mt_allow_pings'] == 1
        return postObj
        
    def _filterCategory(self, cat):
        """Transform category struct in WordPressCategory instance
        """
        catObj = WordPressCategory()
        catObj.id             = int(cat['categoryId'])
        catObj.name         = cat['categoryName'] 
        if cat.has_key('isPrimary'):
            catObj.isPrimary     = cat['isPrimary']
        return catObj
    
    def _filterAuthors(self, cat):
        userObj = WordPressAuthors()
        userObj.id    = int(cat['user_id'])
        userObj.name  = cat['display_name'] 
        userObj.login = cat['user_login']
        return userObj
    
    #WP getCategorie according to http://codex.wordpress.org/XML-RPC_wp#wp.getCategories
    #unable to use that shit because WP doesn't provide slug !!!! FUCK U WP
    def _filterWPCategory(self,cat):
        """Transform category struct in WordPressCategory instance
        """
        catObj = WordPressCategory()
        catObj.id             = int(cat['categoryId'])
        catObj.pid             = int(cat['parentId'])
        catObj.name         = cat['categoryName'] 
        catObj.niceName     = cat['categorySlug']
        if cat.has_key('isPrimary'):
            catObj.isPrimary     = cat['isPrimary']
        return catObj
    
    #WP getCategorie according to http://codex.wordpress.org/XML-RPC_wp#wp.getCategories
    def _filterWPTags(self,tag):
        """Transform category struct in WordPressCategory instance
        """
        tagObj = WordPressTag()
        tagObj.id   = int(tag['tag_id'])
        tagObj.name = tag['name'] 
        tagObj.slug = tag['slug']
        return tagObj
    
    def _filterWPComments(self,com):
        """Transform category struct in WordPressCategory instance
        """
        tagObj = WordPressComments()
        tagObj.id      = int(com['comment_id'])
        tagObj.status  = com['status'] 
        tagObj.content = com['content']
        tagObj.link    = com['link']
        tagObj.post_id = com['post_id'] 
        tagObj.author  = com['author'] 
        tagObj.au_mail = com['author_email']
        tagObj.au_url  = com['author_url']
        tagObj.au_ip   = com['author_ip']
        tagObj.date    = datetime.datetime.strptime(str(com['date_created_gmt']), "%Y%m%dT%H:%M:%S")
        return tagObj
        
    def selectBlog(self, blogId):
        self.blogId = blogId
        
    def supportedMethods(self):
        """Get supported methods list
        """
        return self._server.mt.supportedMethods()

    def getLastPost(self):
        """Get last post
        """
        return tuple(self.getRecentPosts(1))[0]
            
    def getRecentPosts(self, numPosts):
        """Get recent posts
        """
        try:
            posts = self._server.metaWeblog.getRecentPosts(self.blogId, self.user, 
                                                    self.password, numPosts)
            for post in posts:
                yield self._filterPost(post)    
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def getPost(self, postId):
        """Get post item
        """
        try:
            return self._filterPost(self._server.metaWeblog.getPost(str(postId), self.user, self.password))
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
    def getUserInfo(self):
        """Get user info
        """
        try:
            userinfo = self._server.blogger.getUserInfo('', self.user, self.password)
            userObj = WordPressUser()
            userObj.id = userinfo['userid']
            userObj.firstName = userinfo['firstname']
            userObj.lastName = userinfo['lastname']
            userObj.nickname = userinfo['nickname']
            userObj.email = userinfo['email']
            return userObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def getUsersBlogs(self):
        """Get blog's users info
        """
        try:
            blogs = self._server.blogger.getUsersBlogs('', self.user, self.password)
            for blog in blogs:
                blogObj = WordPressBlog()
                blogObj.id = blog['blogid']
                blogObj.name = blog['blogName']
                blogObj.isAdmin = blog['isAdmin']
                blogObj.url = blog['url']
                yield blogObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
    def getAuthors(self):
        """Get blog's users info
        """
        try:
            if not self.authors:
                self.authors = []
                #categories = self._server.mt.getCategoryList(self.blogId, self.user, self.password)                
                authors = self._server.wp.getAuthors(self.blogId, self.user, self.password)                
                for aut in authors:
                    self.authors.append(self._filterAuthors(aut))    
            return self.authors
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def newPost(self, post, publish):
        """Insert new post
        """
        blogContent = {
            'title' : post.title,
            'description' : post.description    
        }
        
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1
        
        # insert new post
        idNewPost = int(self._server.metaWeblog.newPost(self.blogId, self.user, self.password, blogContent, 0))
        
        # set categories for new post
        self.setPostCategories(idNewPost, categories)
        
        # publish post if publish set at True 
        if publish:
            self.publishPost(idNewPost)
            
        return idNewPost
       
    def getPostCategories(self, postId):
        """Get post's categories
        """
        try:
            categories = self._server.mt.getPostCategories(postId, self.user, 
                                                    self.password)
            for cat in categories:
                yield self._filterCategory(cat)    
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def setPostCategories(self, postId, categories):
        """Set post's categories
        """
        self._server.mt.setPostCategories(postId, self.user, self.password, categories)
    
    def editPost(self, postId, post, publish):
        """Edit post
        """
        blogcontent = {
            'title' : post.title,
            'description' : post.description,
            'permaLink' : post.permaLink,
            'mt_allow_pings' : post.allowPings,
            'mt_text_more' : post.textMore,
            'mt_excerpt' : post.excerpt
        }
        
        if post.date:
            blogcontent['dateCreated'] = xmlrpclib.DateTime(post.date) 
        
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1                 
        
        result = self._server.metaWeblog.editPost(postId, self.user, self.password,
                                              blogcontent, 0)
        
        if result == 0:
            raise WordPressException('Post edit failed')
            
        # set categories for new post
        self.setPostCategories(postId, categories)
        
        # publish new post
        if publish:
            self.publishPost(postId)

    def deletePost(self, postId):
        """Delete post
        """
        try:
            return self._server.blogger.deletePost('', postId, self.user, 
                                             self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategoryList(self):
        """Get blog's categories list
        """
        try:
            if not self.categories:
                self.categories = []
                #categories = self._server.mt.getCategoryList(self.blogId, self.user, self.password)                
                categories = self._server.wp.getCategories(self.blogId, self.user, self.password)                
                for cat in categories:
                    self.categories.append(self._filterWPCategory(cat))    
            return self.categories
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)    
            
    def getTagList(self):
        """Get blog's tag list
        """
        try:
            if not self.tags:
                self.tags = []
                tags = self._server.wp.getTags(self.blogId, self.user, self.password)                
                for t in tags:
                    self.tags.append(self._filterWPTags(t))    
            return self.tags
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
    def getCommentList(self,post_id,limit=10):
        """Get blog's tag list
        """
        try:
            if not self.comments:
                self.comments = []
                comments = self._server.wp.getComments(self.blogId, self.user, self.password,{'post_id':post_id,'number':limit})                
                for t in comments:
                    self.comments.append(self._filterWPComments(t))    
            return self.comments
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategoryIdFromName(self, name):
        """Get category id from category name
        """
        for c in self.getCategoryList():
            if c.name == name:
                return c.id
        
    def getTrackbackPings(self, postId):
        """Get trackback pings of post
        """
        try:
            return self._server.mt.getTrackbackPings(postId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def publishPost(self, postId):
        """Publish post
        """
        try:
            return (self._server.mt.publishPost(postId, self.user, self.password) == 1)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getPingbacks(self, postUrl):
        """Get pingbacks of post
        """
        try:
            return self._server.pingback.extensions.getPingbacks(postUrl)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def newMediaObject(self, mediaFileName):
        """Add new media object (image, movie, etc...)
        """
        try:
            f = file(mediaFileName, 'rb')
            mediaBits = f.read()
            f.close()
            
            mediaStruct = {
                'name' : os.path.basename(mediaFileName),
                'bits' : xmlrpclib.Binary(mediaBits)
            }
            
            result = self._server.metaWeblog.newMediaObject(self.blogId, 
                                    self.user, self.password, mediaStruct)
            return result['url']
            
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    