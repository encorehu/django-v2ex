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
from google.appengine.api.labs import taskqueue

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

class MoneyDashboardHandler(BaseHandler):
    def get(self, request):
        if self.member:
            self.set_title(u'账户查询')
            self.finalize(template_name='money_dashboard')
        else:
            #self.redirect('/signin')

def main():
    application = webapp.WSGIApplication([
    ('/money/dashboard/?', MoneyDashboardHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()