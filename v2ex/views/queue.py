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

class AddStarTopicHandler(View):
    def post(self, request, topic_key):
        topic = db.get(db.Key(topic_key))
        if topic:
            topic.stars = topic.stars + 1
            topic.save()
            cache.set('Topic_' + str(topic.num), topic, 86400)

class MinusStarTopicHandler(View):
    def post(self, request, topic_key):
        topic = db.get(db.Key(topic_key))
        if topic:
            topic.stars = topic.stars - 1
            topic.save()
            cache.set('Topic_' + str(topic.num), topic, 86400)


def main():
    application = webapp.WSGIApplication([
    ('/add/star/topic/(.*)', AddStarTopicHandler),
    ('/minus/star/topic/(.*)', MinusStarTopicHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()