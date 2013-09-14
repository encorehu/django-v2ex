#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import string
import random
import urllib
import urllib2


from django.core.cache import cache
from google.appengine.api import urlfetch
from django.db import models
#from google.appengine.ext.webapp import util
from django import template

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

from django.utils import simplejson as json

template.register_template_library('v2ex.templatetags.filters')

class ImagesHomeHandler(View):
    def get(self, request):
        site = GetSite()
        browser = detect(self.request)
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        self.session = Session()
        if member:
            source = 'http://daydream/stream/' + str(member.num)
            result = urlfetch.fetch(source)
            images = json.loads(result.content)
            template_values = {}
            template_values['images'] = images
            template_values['site'] = site
            template_values['member'] = member
            template_values['page_title'] = site.title + u' › 图片上传'
            template_values['l10n'] = l10n
            template_values['system_version'] = SYSTEM_VERSION
            if 'message' in self.session:
                template_values['message'] = self.session['message']
                del self.session['message']
            path = 'desktop/images_home.html'
            #output = template.render(path, template_values)
            #self.response.out.write(output)
            return render(request, path, template_values)
        else:
            #self.redirect('/signin')

class ImagesUploadHandler(View):
    def post(self, request):
        site = GetSite()
        browser = detect(self.request)
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        if member:    
            image = self.request.GET.get('image')
            if image is not None:
                import urllib, urllib2
                parameters = urllib.urlencode(dict(member_id=member.num, image=image))
                try:
                    f = urllib2.urlopen('http://daydream/upload', parameters)
                    data = f.read()
                    f.close()
                except:
                    self.session = Session()
                    self.session['message'] = '图片不能超过 1M'
                #self.redirect('/images')
        else:
            #self.redirect('/signin')

class ImagesUploadRulesHandler(View):
    def get(self, request):
        site = GetSite()
        browser = detect(self.request)
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)   
        template_values = {}
        template_values['site'] = site
        template_values['member'] = member
        template_values['page_title'] = site.title + u' › 图片上传规则'
        template_values['l10n'] = l10n
        template_values['system_version'] = SYSTEM_VERSION
        path = 'desktop/images_rules.html'
        output = template.render(path, template_values)
        self.response.out.write(output)
        

def main():
    application = webapp.WSGIApplication([
    ('/images/upload', ImagesUploadHandler),
    ('/images/upload/rules', ImagesUploadRulesHandler),
    ('/images/?', ImagesHomeHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()