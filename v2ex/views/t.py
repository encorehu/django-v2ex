#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import string
import random
import logging


from django.core.cache import cache
from django.db import models
#from google.appengine.ext.webapp import util
from django import template
from django import template
from django.views.generic import View, ListView,TemplateView
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect

from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Note

from v2ex.babel.models import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session

from twitter.oauthtwitter import OAuthApi
from twitter.oauth import OAuthToken

from v2ex.config import twitter_consumer_key as CONSUMER_KEY
from v2ex.config import twitter_consumer_secret as CONSUMER_SECRET

#template.register_template_library('v2ex.templatetags.filters')

class TwitterLinkHandler(View):
    def get(self, request):
        self.session = Session()
        member = CheckAuth(self)
        if member:
            twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)
            request_token = twitter.getRequestToken()
            authorization_url = twitter.getAuthorizationURL(request_token)
            self.session['request_token'] = request_token
            self.redirect(authorization_url)
        else:
            #self.redirect('/signin')
            return redirect('/signin')

class TwitterUnlinkHandler(View):
    def get(self, request):
        self.session = Session()
        member = CheckAuth(self)
        if member:
            cache.delete('Member_' + str(member.num))
            member = GetKindByNum('Member', member.num)
            member.twitter_oauth = 0
            member.twitter_oauth_key = ''
            member.twitter_oauth_secret = ''
            member.twitter_sync = 0
            member.save()
            cache.set('Member_' + str(member.num), member, 86400)
            #self.redirect('/settings')
            return redirect('/settings')
        else:
            #self.redirect('/signin')
            return redirect('/signin')

class TwitterCallbackHandler(View):
    def get(self, request):
        self.session = Session()
        member = CheckAuth(self)
        host = self.request.META['Host']
        if host == 'localhost:10000' or host == '127.0.0.1:10000':
            # Local debugging logic
            if member:
                request_token = self.session['request_token']
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, request_token)
                access_token = twitter.getAccessToken()
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                user = twitter.GetUserInfo()
                cache.delete('Member_' + str(member.num))
                member = db.get(member.key())
                member.twitter_oauth = 1
                member.twitter_oauth_key = access_token.key
                member.twitter_oauth_secret = access_token.secret
                member.twitter_oauth_string = access_token.to_string()
                member.twitter_sync = 0
                member.twitter_id = user.id
                member.twitter_name = user.name
                member.twitter_screen_name = user.screen_name
                member.twitter_location = user.location
                member.twitter_description = user.description
                member.twitter_profile_image_url = user.profile_image_url
                member.twitter_url = user.url
                member.twitter_statuses_count = user.statuses_count
                member.twitter_followers_count = user.followers_count
                member.twitter_friends_count = user.friends_count
                member.twitter_favourites_count = user.favourites_count
                member.save()
                cache.set('Member_' + str(member.num), member, 86400)
                #self.redirect('/settings')
                return redirect('/settings')
            else:
                #self.redirect('/signin')
                return redirect('/signin')
        else:
            # Remote production logic
            if member and 'request_token' in self.session:
                request_token = self.session['request_token']
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, request_token)
                access_token = twitter.getAccessToken()
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                user = twitter.GetUserInfo()
                cache.delete('Member_' + str(member.num))
                member = db.get(member.key())
                member.twitter_oauth = 1
                member.twitter_oauth_key = access_token.key
                member.twitter_oauth_secret = access_token.secret
                member.twitter_oauth_string = access_token.to_string()
                member.twitter_sync = 0
                member.twitter_id = user.id
                member.twitter_name = user.name
                member.twitter_screen_name = user.screen_name
                member.twitter_location = user.location
                member.twitter_description = user.description
                member.twitter_profile_image_url = user.profile_image_url
                member.twitter_url = user.url
                member.twitter_statuses_count = user.statuses_count
                member.twitter_followers_count = user.followers_count
                member.twitter_friends_count = user.friends_count
                member.twitter_favourites_count = user.favourites_count
                member.save()
                cache.set('Member_' + str(member.num), member, 86400)
                #self.redirect('/settings')
                return redirect('/settings')
            else:
                oauth_token = self.request.get('oauth_token')
                if host == 'v2ex.appspot.com':
                    #self.redirect()
                    return redirect('http://localhost:8000/twitter/oauth?oauth_token=' + oauth_token)
                else:
                    #self.redirect()   
                    return redirect('http://localhost:8000/twitter/oauth?oauth_token=' + oauth_token)     

class TwitterHomeHandler(View):
    def get(self, request):
        site = GetSite()
        member = CheckAuth(self)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(self, member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Home'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                rate_limit = cache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        cache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::home'
                statuses = cache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetHomeTimeline(count = 50)
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a class="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    cache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = 'desktop/twitter_home.html'
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                #self.redirect('/settings')
                return redirect('/settings')
        else:
            #self.redirect('/')
            return redirect('/')

class TwitterMentionsHandler(View):
    def get(self, request):
        site = GetSite()
        member = CheckAuth(self)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(self, member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Mentions'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                rate_limit = cache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        cache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::mentions'
                statuses = cache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetReplies()
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a class="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    cache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = 'desktop/twitter_mentions.html'
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                #self.redirect('/settings')
                return redirect('/settings')
        else:
            #self.redirect('/')
            return redirect('/')

class TwitterDMInboxHandler(View):
    def get(self, request):
        member = CheckAuth(self)
        site = GetSite()
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(self, member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Direct Messages › Inbox'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                rate_limit = cache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        cache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::dm::inbox'
                messages = cache.get(cache_tag)
                if messages is None:
                    messages = twitter.GetDirectMessages()
                    i = 0;
                    for message in messages:
                        messages[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(message.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        messages[i].text = twitter.ConvertMentions(message.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    cache.set(cache_tag, messages, 120)
                template_values['messages'] = messages
                path = 'desktop/twitter_dm_inbox.html'
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                #self.redirect('/settings')
                return redirect('/settings')
        else:
            #self.redirect('/')
            return redirect('/')

class TwitterUserTimelineHandler(View):
    def get(self, request, screen_name):
        site = GetSite()
        member = CheckAuth(self)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(self, member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › ' + screen_name
                template_values['screen_name'] = screen_name
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                rate_limit = cache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        cache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'twitter::' + screen_name + '::home'
                statuses = cache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetUserTimeline(user=screen_name, count = 50)
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a class="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    cache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = 'desktop/twitter_user.html'
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                #self.redirect('/settings')
                return redirect('/settings')
        else:
            #self.redirect('/')
            return redirect('/')
                        
class TwitterTweetHandler(View):
    def post(self, request):
        if 'HTTP_REFERER' in self.request.META:
            go = self.request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(self)
        if member:
            if member.twitter_oauth == 1:
                status = self.request.get('status')
                if len(status) > 140:
                    status = status[0:140]
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                try:
                    twitter.PostUpdate(status.encode('utf-8'))
                    cache.delete('member::' + str(member.num) + '::twitter::home')
                except:
                    logging.error('Failed to tweet: ' + status)
                self.redirect(go)
            else:
                #self.redirect('/twitter/link')
                return redirect('/twitter/link')
        else:
            #self.redirect('/')
            return redirect('/')
        
class TwitterApiCheatSheetHandler(View):
    def head(self):
        template_values = {}
        path = 'desktop/twitter_api_cheat_sheet.html'
        output = template.render(path, template_values)
        self.response.out.write(output)
        
    def get(self, request):
        template_values = {}
        path = 'desktop/twitter_api_cheat_sheet.html'
        output = template.render(path, template_values)
        self.response.out.write(output)
        
def main():
    application = webapp.WSGIApplication([
    ('/twitter/?', TwitterHomeHandler),
    ('/twitter/mentions/?', TwitterMentionsHandler),
    ('/twitter/inbox/?', TwitterDMInboxHandler),
    ('/twitter/user/([a-zA-Z0-9\_]+)', TwitterUserTimelineHandler),
    ('/twitter/link', TwitterLinkHandler),
    ('/twitter/unlink', TwitterUnlinkHandler),
    ('/twitter/oauth', TwitterCallbackHandler),
    ('/twitter/tweet', TwitterTweetHandler),
    ('/twitter/api/?', TwitterApiCheatSheetHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()