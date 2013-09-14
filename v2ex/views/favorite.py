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
#from google.appengine.ext.webapp import util
from django import template
#from google.appengine.api.labs import taskqueue

from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect
from django.conf import settings
from django.utils import timezone

from django.views.generic import View, ListView,TemplateView

from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Note
from v2ex.babel.models import NodeBookmark
from v2ex.babel.models import TopicBookmark
from v2ex.babel.models import MemberBookmark

from v2ex.babel.models import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *

from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session

class FavoriteNodeHandler(View):
    def get(self, request, node_name):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t')
        if member:
            if str(member.created_ts) == str(t):
                node = GetKindByName('Node', node_name)
                if node is not False:
                    #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE node = :1 AND member = :2", node, member)
                    q = NodeBookmark.objects.filter(node = node, member = member)
                    if q.count() == 0:
                        #bookmark = NodeBookmark(parent=member)
                        bookmark = NodeBookmark(member=member)
                        bookmark.node = node
                        bookmark.member = member
                        bookmark.save()
                        member = db.get(member.key())
                        member.favorited_nodes = member.favorited_nodes + 1
                        member.save()
                        cache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/n' + str(node.num) + '/m' + str(member.num)
                        cache.set(n, True, 86400 * 14)
        #self.redirect(go)
        return redirect(go)
    
class UnfavoriteNodeHandler(View):
    def get(self, request, node_name):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t')
        if member:
            if str(member.created_ts) == str(t):
                node = GetKindByName('Node', node_name)
                if node is not False:
                    #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE node = :1 AND member = :2", node, member)
                    q = NodeBookmark.objects.filter(node = node, member = member)
                    if q.count() > 0:
                        bookmark = q[0]
                        bookmark.delete()
                        member = db.get(member.key())
                        member.favorited_nodes = member.favorited_nodes - 1
                        member.save()
                        cache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/n' + str(node.num) + '/m' + str(member.num)
                        cache.delete(n)
        #self.redirect(go)
        return redirect(go)

class FavoriteTopicHandler(View):
    def get(self, request, topic_num):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t').strip()
        if member:
            if member.username_lower_md5 == t:
                topic = GetKindByNum('Topic', int(topic_num))
                if topic is not False:
                    #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic = :1 AND member = :2", topic, member)
                    q = TopicBookmark.objects.filter(topic = topic, member = member)
                    if q.count() == 0:
                        #bookmark = TopicBookmark(parent=member)
                        bookmark = TopicBookmark(member=member)
                        bookmark.topic = topic
                        bookmark.member = member
                        bookmark.save()
                        #member = db.get(member.key())
                        member.favorited_topics = member.favorited_topics + 1
                        member.save()
                        cache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                        cache.set(n, True, 86400 * 14)
                        #taskqueue.add(url='/add/star/topic/' + str(topic.key()))
        #self.redirect(go)
        return redirect(go)

class UnfavoriteTopicHandler(View):
    def get(self, request, topic_num):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t').strip()
        if member:
            if member.username_lower_md5 == t:
                topic = GetKindByNum('Topic', int(topic_num))
                if topic is not False:
                    #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic = :1 AND member = :2", topic, member)
                    q = TopicBookmark.objects.filter(topic = topic, member = member)
                    if q.count() > 0:
                        bookmark = q[0]
                        bookmark.delete()
                        member = db.get(member.key())
                        member.favorited_topics = member.favorited_topics - 1
                        member.save()
                        cache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                        cache.delete(n)
                        #taskqueue.add(url='/minus/star/topic/' + str(topic.key()))
        #self.redirect(go)
        return redirect(go)
        
class FollowMemberHandler(View):
    def get(self, request, one_num):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t')
        if member:
            if str(member.created_ts) == str(t):
                one = GetKindByNum('Member', int(one_num))
                if one is not False:
                    if one.num != member.num:
                        #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE one = :1 AND member_num = :2", one, member.num)
                        q = MemberBookmark.objects.filter(one = one, member_num = member.num)
                        if q.count() == 0:
                            #member = db.get(member.key())
                            member.favorited_members = member.favorited_members + 1
                            if member.favorited_members > 30:
                                self.session = Session()
                                self.session['message'] = '最多只能添加 30 位特别关注'
                            else:
                                #bookmark = MemberBookmark(parent=member)
                                bookmark = MemberBookmark()
                                bookmark.one = one
                                bookmark.member_num = member.num
                                bookmark.save()
                                member.save()
                                cache.set('Member_' + str(member.num), member, 86400)
                                n = 'r/m' + str(one.num) + '/m' + str(member.num)
                                cache.set(n, True, 86400 * 14)
                                #one = db.get(one.key())
                                one.followers_count = one.followers_count + 1
                                one.save()
                                cache.set('Member_' + str(one.num), one, 86400)
                                cache.set('Member::' + str(one.username_lower), one, 86400)
                                self.session = Session()
                                self.session['message'] = '特别关注添加成功，还可以添加 ' + str(30 - member.favorited_members) + ' 位'
        #self.redirect(go)
        return redirect(go)

class UnfollowMemberHandler(View):
    def get(self, request, one_num):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.GET.get('t')
        if member:
            if str(member.created_ts) == str(t):
                one = GetKindByNum('Member', int(one_num))
                if one is not False:
                    if one.num != member.num:
                        #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE one = :1 AND member_num = :2", one, member.num)
                        q = MemberBookmark.objects.filter(one = one, member_num = member.num)
                        if q.count() > 0:
                            bookmark = q[0]
                            bookmark.delete()
                            #member = db.get(member.key())
                            member.favorited_members = member.favorited_members - 1
                            member.save()
                            cache.set('Member_' + str(member.num), member, 86400)
                            n = 'r/m' + str(one.num) + '/m' + str(member.num)
                            cache.delete(n)
                            #one = db.get(one.key())
                            one.followers_count = one.followers_count - 1
                            one.save()
                            cache.set('Member_' + str(one.num), one, 86400)
                            cache.set('Member::' + str(one.username_lower), one, 86400)
        #self.redirect(go)
        return redirect(go)

def main():
    application = webapp.WSGIApplication([
    ('/favorite/node/([a-zA-Z0-9]+)', FavoriteNodeHandler),
    ('/unfavorite/node/([a-zA-Z0-9]+)', UnfavoriteNodeHandler),
    ('/favorite/topic/([0-9]+)', FavoriteTopicHandler),
    ('/unfavorite/topic/([0-9]+)', UnfavoriteTopicHandler),
    ('/follow/([0-9]+)', FollowMemberHandler),
    ('/unfollow/([0-9]+)', UnfollowMemberHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()