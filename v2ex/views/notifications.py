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
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect
from django.conf import settings

from django.db import models
##from google.appengine.ext.webapp import util
from django import template
from django.views.generic import View, ListView,TemplateView

#from google.appengine.api.labs import taskqueue

from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Note
from v2ex.babel.models import Notification

from v2ex.babel.models import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies

from v2ex.babel.handlers import BaseHandler

from v2ex import config

#template.register_template_library('v2ex.templatetags.filters')

class NotificationsHandler(BaseHandler):
    def get(self, request):
        member = CheckAuth(self)
        if member:
            if member.private_token is None:
                member.private_token = hashlib.sha256(str(member.num) + ';' + config.site_key).hexdigest()
                member.save()
            notifications = cache.get('nn::' + member.username_lower)
            if notifications is None:
                #q = db.GqlQuery("SELECT * FROM Notification WHERE for_member_num = :1 ORDER BY num DESC LIMIT 20", member.num)
                q = Notification.objects.filter(for_member_num = member.num).order_by('-num')[:20]
                notifications = []
                i = 0
                for n in q:
                    if i == 0:
                        if member.notification_position != n.num:
                            member.notification_position = n.num
                            member.save()
                    if n.type == 'reply':
                        n.text = u'<a href="/member/' + n.member.username + u'"><strong>' + n.member.username + u'</strong></a> 在 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 里回复了你'
                        notifications.append(n)
                    if n.type == 'mention_reply':
                        n.text = u'<a href="/member/' + n.member.username + u'"><strong>' + n.member.username + u'</strong></a> 在回复 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    if n.type == 'mention_topic':
                        n.text = u'<a href="/member/' + n.member.username + u'"><strong>' + n.member.username + u'</strong></a> 在创建主题 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    i = i + 1
                member.notifications = 0
                member.save()
                cache.set('Member_' + str(member.num), member, 86400)
                cache.set('nn::' + member.username_lower, notifications, 360)
            self.values['notifications'] = notifications
            self.set_title(u'提醒系统')
            return self.finalize(template_name='notifications', mobile_optimized=True)
        else:
            #self.redirect('/signin')
            return redirect('/signin')
            

class NotificationsCheckHandler(BaseHandler):
    def post(self, request, member_key):
        member = db.get(db.Key(member_key))
        if member:
            if member.notification_position is None:
                member.notification_position = 0
            #q = db.GqlQuery("SELECT __key__ FROM Notification WHERE for_member_num = :1 AND num > :2 ORDER BY num DESC", member.num, member.notification_position)
            q = Notification.objects.filter(for_member_num = member.num, num__gt=member.notification_position).order_by('-num')
            count = q.count()
            if count > 0:
                member.notifications = count
                member.save()
                cache.delete('nn::' + member.username_lower)
                cache.set('Member_' + str(member.num), member, 86400)

# For mentions in reply content
class NotificationsReplyHandler(BaseHandler):
    def post(self, request, reply_key):
        reply = db.get(db.Key(reply_key))
        topic = GetKindByNum('Topic', reply.topic_num)
        ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', reply.content)
        unique = []
        for m in ms:
            if m.lower() not in unique:
                unique.append(m.lower())
        keys = []
        if (len(unique) > 0):
            for m in unique:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        member_username = m_id[0]
                        member = GetMemberByUsername(member_username)
                        if member:
                            if (member.key() != topic.member.key()) and (member.key() != reply.member.key()) and (member.key() not in keys):
                                q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.max')
                                if (q.count() == 1):
                                    counter = q[0]
                                    counter.value = counter.value + 1
                                else:
                                    counter = Counter()
                                    counter.name = 'notification.max'
                                    counter.value = 1
                                q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.total')
                                if (q2.count() == 1):
                                    counter2 = q2[0]
                                    counter2.value = counter2.value + 1
                                else:
                                    counter2 = Counter()
                                    counter2.name = 'notification.total'
                                    counter2.value = 1

                                #notification = Notification(parent=member)
                                notification = Notification(member=member)
                                notification.num = counter.value
                                notification.type = 'mention_reply'
                                notification.payload = reply.content
                                notification.label1 = topic.title
                                notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                                notification.member = reply.member
                                notification.for_member_num = member.num

                                keys.append(str(member.key()))

                                counter.save()
                                counter2.save()
                                notification.save()
        ###for k in keys:
        ###    taskqueue.add(url='/notifications/check/' + k)

# For mentions in topic title and content
class NotificationsTopicHandler(BaseHandler):
    def post(self, request, topic_key):
        topic = db.get(db.Key(topic_key))
        combined = topic.title + " " + topic.content
        ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', combined)
        unique = []
        for m in ms:
            if m.lower() not in unique:
                unique.append(m.lower())
        keys = []
        if (len(unique) > 0):
            for m in unique:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        member_username = m_id[0]
                        member = GetMemberByUsername(member_username)
                        if member:
                            if member.key() != topic.member.key() and member.key() not in keys:
                                q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.max')
                                if (q.count() == 1):
                                    counter = q[0]
                                    counter.value = counter.value + 1
                                else:
                                    counter = Counter()
                                    counter.name = 'notification.max'
                                    counter.value = 1
                                q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.total')
                                if (q2.count() == 1):
                                    counter2 = q2[0]
                                    counter2.value = counter2.value + 1
                                else:
                                    counter2 = Counter()
                                    counter2.name = 'notification.total'
                                    counter2.value = 1

                                #notification = Notification(parent=member)
                                notification = Notification(member=member)
                                notification.num = counter.value
                                notification.type = 'mention_topic'
                                notification.payload = topic.content
                                notification.label1 = topic.title
                                notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                                notification.member = topic.member
                                notification.for_member_num = member.num

                                keys.append(str(member.key()))

                                counter.save()
                                counter2.save()
                                notification.save()
        ###for k in keys:
        ###    taskqueue.add(url='/notifications/check/' + k)

class NotificationsFeedHandler(BaseHandler):
    def head(self, private_token):
        pass
            
    def get(self, request, private_token):
        n = cache.get('n_' + private_token)
        if n is not None:
            self.values['notification'] = n
            self.response.headers['Content-type'] = 'application/xml;charset=UTF-8'
            self.values['member'] = member
            self.finalize(template_name='notifications', template_root='feed', template_type='xml')
        else:
            q = db.GqlQuery("SELECT * FROM Member WHERE private_token = :1", private_token)
            count = q.count()
            if count > 0:
                member = q[0]
                q = db.GqlQuery("SELECT * FROM Notification WHERE for_member_num = :1 ORDER BY num DESC LIMIT 20", member.num)
                notifications = []
                i = 0
                for n in q:
                    if n.type == 'reply':
                        n.title = u'' + n.member.username + u' 在 ' + self.escape(n.label1) + u' 里回复了你'
                        n.text = u'<a href="/member/' + n.member.username + u'"><strong>' + n.member.username + u'</strong></a> 在 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 里回复了你'
                        notifications.append(n)
                    if n.type == 'mention_reply':
                        n.title = u'' + n.member.username + u' 在回复 ' + self.escape(n.label1) + u' 时提到了你'
                        n.text = u'<a href="/member/' + n.member.username + u'"><strong>' + n.member.username + u'</strong></a> 在回复 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    i = i + 1
                self.values['notifications'] = notifications
                cache.set('n_' + private_token, notifications, 600)
                self.response.headers['Content-type'] = 'application/xml;charset=UTF-8'
                self.values['site'] = GetSite()
                self.values['member'] = member
                self.finalize(template_name='notifications', template_root='feed', template_type='xml')

def main():
    application = webapp.WSGIApplication([
    ('/notifications/?', NotificationsHandler),
    ('/notifications/check/(.+)', NotificationsCheckHandler),
    ('/notifications/reply/(.+)', NotificationsReplyHandler),
    ('/notifications/topic/(.+)', NotificationsTopicHandler),
    ('/n/([a-z0-9]+).xml', NotificationsFeedHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()