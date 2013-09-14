#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import string
import random


from django.core.cache import cache
from django.db import models
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect
from django.conf import settings

from django.db import models
##from google.appengine.ext.webapp import util
from django import template
from django.views.generic import View, ListView,TemplateView


from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Note
from v2ex.babel.models import MemberBookmark

from v2ex.babel.models import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session

#template.register_template_library('v2ex.templatetags.filters')

class MyNodesHandler(View):
    def get(self, request):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的节点'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_nodes > 0:
                template_values['has_nodes'] = True
                q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE member = :1 ORDER BY created DESC LIMIT 0,15", member)
                template_values['column_1'] = q
                if member.favorited_nodes > 15:
                    q2 = db.GqlQuery("SELECT * FROM NodeBookmark WHERE member = :1 ORDER BY created DESC LIMIT 15,15", member)
                    template_values['column_2'] = q2
            else:
                template_values['has_nodes'] = False
            path = 'desktop/my_nodes.html'
            #output = template.render(path, template_values)
            #self.response.out.write(output)
            return render(request, path, template_values)
        else:
            #self.redirect('/')
            return redirect('/')

class MyTopicsHandler(View):
    def get(self, request):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的主题'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_topics > 0:
                template_values['has_topics'] = True
                q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE member = :1 ORDER BY created DESC", member)
                bookmarks = []
                for bookmark in q:
                    try:
                        topic = bookmark.topic
                        bookmarks.append(bookmark)
                    except:
                        bookmark.delete()
                template_values['bookmarks'] = bookmarks
            else:
                template_values['has_topics'] = False
            path = 'desktop/my_topics.html'
            #output = template.render(path, template_values)
            #self.response.out.write(output)
            return render(request, path, template_values)
        else:
            #self.redirect('/')
            return redirect('/')
            
class MyFollowingHandler(View):
    def get(self, request):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我的特别关注'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_members > 0:
                template_values['has_following'] = True
                #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE member_num = :1 ORDER BY created DESC", member.num)
                q = MemberBookmark.objects.filter(member_num = member.num).order_by('-created')
                template_values['following'] = q
                following = []
                for bookmark in q:
                    following.append(bookmark.one.num)
                #q2 = db.GqlQuery("SELECT * FROM Topic WHERE member_num IN :1 ORDER BY created DESC LIMIT 20", following)
                q2 = Topic.objects.filter(member_num__in = following).order_by('-created')[:20]
                template_values['latest'] = q2
            else:
                template_values['has_following'] = False
            path = 'desktop/my_following.html'
            #output = template.render(path, template_values)
            #self.response.out.write(output)
            return render(request, path, template_values)
        else:
            #self.redirect('/')
            return redirect('/')

def main():
    application = webapp.WSGIApplication([
    ('/my/nodes', MyNodesHandler),
    ('/my/topics', MyTopicsHandler),
    ('/my/following', MyFollowingHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()