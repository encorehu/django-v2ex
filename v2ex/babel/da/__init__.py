# coding=utf-8
# "da" means Data Access, this file contains various quick (or dirty) methods for accessing data.

import hashlib
import logging
import zlib
import pickle

from django.db import models
from django.core.cache import cache

from v2ex.babel.models import Member
from v2ex.babel.models import Counter
from v2ex.babel.models import Section
from v2ex.babel.models import Node
from v2ex.babel.models import Topic
from v2ex.babel.models import Reply
from v2ex.babel.models import Place
from v2ex.babel.models import Site

def GetKindByNum(kind, num):
    K = str(kind.capitalize())
    one = cache.get(K + '_' + str(num))
    if one:
        return one
    else:
        #q = models.GqlQuery("SELECT * FROM " + K + " WHERE num = :1", int(num))
        try:
            app_label = 'babel'
            model_name = K
            print app_label, model_name
            TheModel = models.get_model(app_label, model_name,seed_cache=False)
            print TheModel
        except ImportError:
            raise Exception('Import Error')
        q = TheModel.objects.filter(num = int(num))
            
        if q.count() == 1:
            one = q[0]
            cache.set(K + '_' + str(num), one, 86400)
            return one
        else:
            return False
            
def GetKindByName(kind, name):
    K = str(kind.capitalize())
    one = cache.get(K + '::' + str(name))
    if one:
        return one
    else:
        #q = models.GqlQuery("SELECT * FROM " + K + " WHERE name = :1", str(name))
        
        try:
            app_label = 'babel'
            model_name = K
            print app_label, model_name
            TheModel = models.get_model(app_label, model_name,seed_cache=False)
            print TheModel
        except ImportError:
            raise Exception('Import Error')
        
        q = TheModel.objects.filter(name = str(name))
        if q.count() == 1:
            one = q[0]
            cache.set(K + '::' + str(name), one, 86400)
            return one
        else:
            return False

def GetMemberByUsername(name):
    one = cache.get('Member::' + str(name).lower())
    if one:
        return one
    else:
        #q = models.GqlQuery("SELECT * FROM Member WHERE username_lower = :1", str(name).lower())
        q = Member.objects.filter(username_lower = str(name).lower())
        if q.count() == 1:
            one = q[0]
            cache.set('Member::' + str(name).lower(), one, 86400)
            return one
        else:
            return False

def GetMemberByEmail(email):
    cache = 'Member::email::' + hashlib.md5(email.lower()).hexdigest()
    one = cache.get(cache)
    if one:
        return one
    else:
        #q = models.GqlQuery("SELECT * FROM Member WHERE email = :1", str(email).lower())
        q = Member.objects.filter(email = str(email).lower())
        if q.count() == 1:
            one = q[0]
            cache.set(cache, one, 86400)
            return one
        else:
            return False

def ip2long(ip):
    ip_array = ip.split('.')
    ip_long = int(ip_array[0]) * 16777216 + int(ip_array[1]) * 65536 + int(ip_array[2]) * 256 + int(ip_array[3])
    return ip_long

def GetPlaceByIP(ip):
    place_cache = 'Place_' + ip
    place = cache.get(place_cache)
    if place:
        return place
    else:
        #q = models.GqlQuery("SELECT * FROM Place WHERE ip = :1", ip)
        q = Place.objects.filter(ip = ip)
        
        if q.count() == 1:
            place = q[0]
            cache.set(cache, place, 86400)
            return place
        else:
            return False

def CreatePlaceByIP(ip):
    place = Place()
    #q = models.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place.max')
    q = Counter.objects.filter(name = 'place.max')
    if (q.count() == 1):
        counter = q[0]
        counter.value = counter.value + 1
    else:
        counter = Counter()
        counter.name = 'place.max'
        counter.value = 1
    #q2 = models.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place.total')
    q2 = Counter.objects.filter(name = 'place.total')
    if (q2.count() == 1):
        counter2 = q2[0]
        counter2.value = counter2.value + 1
    else:
        counter2 = Counter()
        counter2.name = 'place.total'
        counter2.value = 1
    place.num = ip2long(ip)
    place.ip = ip
    place.save()
    counter.save()
    counter2.save()
    return place

def GetSite():
    site = cache.get('site')
    if site is not None:
        return site
    else:
        q = Site.objects.all() #("SELECT * FROM Site WHERE num = 1")
        if q.count() >= 1:
            site = q[0]
            if site.l10n is None:
                site.l10n = 'en'
            if site.meta is None:
                site.meta = ''
            cache.set('site', site, 86400)
            return site
        else:
            site = Site()
            site.num = 1
            site.title = 'DJANGO-V2EX'
            site.domain = 'localhost:8000' #'www.v2ex.com'
            site.slogan = 'v2ex way to explore django'
            site.l10n = 'en'
            site.description = 'Python shake, Code rock!'
            site.meta = ''
            site.home_categories = u'\u5206\u4eab\u4e0e\u63a2\u7d22\nV2EX\niOS\nGeek\n\u6e38\u620f\nApple\n\u751f\u6d3b\nInternet\n\u57ce\u5e02\n\u54c1\u724c\n'
            site.save()
            cache.set('site', site, 86400)
            return site

# input is a compressed string
# output is an object
def GetUnpacked(data):
    decompressed = zlib.decompress(data)
    return pickle.loads(decompressed)

# input is an object
# output is an compressed string
def GetPacked(data):
    s = pickle.dumps(data)
    return zlib.compress(s)