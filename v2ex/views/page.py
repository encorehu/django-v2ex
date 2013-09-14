#!/usr/bin/env python
# coding=utf-8

import os
import datetime
import random


from django.core.cache import cache
from django.db import models
#from google.appengine.ext.webapp import util
from django import template
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect
from django.conf import settings

from django.db import models
from django.views.generic import View, ListView,TemplateView

from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Site

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies

#template.register_template_library('v2ex.templatetags.filters')

class AboutHandler(View):
    def get(self, request):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 127)
        if note is False:
            note = GetKindByNum('Note', 2)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › About'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = 'desktop/about.html'
        #output = template.render(path, template_values)
        #self.response.out.write(output)
        return render(request, path, template_values)
        
class FAQHandler(View):
    def get(self, request):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 195)
        if note is False:
            note = GetKindByNum('Note', 4)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › FAQ'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = 'desktop/faq.html'
        #output = template.render(path, template_values)
        #self.response.out.write(output)
        return render(request, path, template_values)

class MissionHandler(View):
    def get(self, request):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 240)
        if note is False:
            note = GetKindByNum('Note', 5)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Mission'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = 'desktop/mission.html'
        #output = template.render(path, template_values)
        #self.response.out.write(output)
        return render(request, path, template_values)

class AdvertiseHandler(View):
    def get(self, request):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Advertise'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = 'desktop/advertise.html'
        #output = template.render(path, template_values)
        #self.response.out.write(output)
        return render(request, path, template_values)

class AdvertisersHandler(View):
    def get(self, request):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Advertisers'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = 'desktop/advertisers.html'
        #output = template.render(path, template_values)
        #self.response.out.write(output)
        return render(request, path, template_values)

def main():
    application = webapp.WSGIApplication([
    ('/about', AboutHandler),
    ('/faq', FAQHandler),
    ('/mission', MissionHandler),
    ('/advertise', AdvertiseHandler),
    ('/advertisers', AdvertisersHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()