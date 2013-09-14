# coding=utf-8

import os
import hashlib
import logging

from django.db import models
from django.core.cache import cache

from v2ex.babel.models import Member

from v2ex.babel.ext.cookies import Cookies

def CheckAuth(handler):
    ip = GetIP(handler)
    cookies = handler.request.COOKIES
    print cookies
    if 'auth' in cookies:
        auth = cookies['auth']
        member_num = cache.get(auth)
        if (member_num > 0):
            member = cache.get('Member_' + str(member_num))
            if member is None:
                q = models.GqlQuery("SELECT * FROM Member WHERE num = :1", member_num)
                if q.count() == 1:
                    member = q[0]
                    cache.set(auth, member.num)
                    cache.set('Member_' + str(member_num), member)
                else:
                    member = False
            if member:
                member.ip = ip
            return member
        else:
            #q = models.GqlQuery("SELECT * FROM Member WHERE auth = :1", auth)
            q = Member.objects.filter(auth = auth)
            if (q.count() == 1):
                member_num = q[0].num
                member = q[0]
                cache.set(auth, member_num)
                cache.set('Member_' + str(member_num), member)
                member.ip = ip
                return member
            else:
                return False
    else:
        return False

def DoAuth(request, destination, message = None):
    if message != None:
        request.session['message'] = message
    else:
        request.session['message'] = u'请首先登入或注册'
    return request.redirect('/signin?destination=' + destination)

def GetIP(handler):
    if 'X-Real-IP' in handler.request.META:
        return handler.request.headers['X-Real-IP']
    else:
        return handler.request.META['REMOTE_ADDR']