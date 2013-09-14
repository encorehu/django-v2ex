#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import urllib
import string
import random


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

from v2ex.babel.models import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session

from django.utils import simplejson as json

from mapreduce import operation as op

def tidy_node(entity):
    # Recalculate exact topics counter
    q = db.GqlQuery("SELECT __key__ FROM Topic WHERE node_num = :1", entity.num)
    entity.topics = q.count()
    cache.set('Node_' + str(entity.num), entity, 86400)
    cache.set('Node::' + entity.name, entity, 86400)
    yield op.db.Put(entity)
    
def tidy_topic(entity):
    # Recalculate exact replies counter
    q = db.GqlQuery("SELECT __key__ FROM Reply WHERE topic_num = :1", entity.num)
    entity.replies = q.count()
    # Ensure member field is correctly set
    q2 = db.GqlQuery("SELECT * FROM Member WHERE num = :1", entity.member_num)
    if q2.count() == 1:
        entity.member = q2[0]
    cache.set('Topic_' + str(entity.num), entity, 86400)
    yield op.db.Put(entity)
    
def tidy_reply(entity):
    # Ensure member field is correctly set
    q = db.GqlQuery("SELECT * FROM Member WHERE num = :1", entity.member_num)
    if q.count() == 1:
        entity.member = q[0]
    # Ensure topic field is correctly set
    q2 = db.GqlQuery("SELECT * FROM Topic WHERE num = :1", entity.topic_num)
    if q2.count() == 1:
        entity.topic = q2[0]
    yield op.db.Put(entity)