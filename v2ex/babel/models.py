SYSTEM_VERSION = '2.5.0-dev-7'

import datetime
import hashlib

import datetime
import os
import random
import shutil
import zipfile
import logging
logger = logging.getLogger("django")

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.core.cache import cache


class Member(models.Model):
    num            = models.IntegerField(db_index=True)
    auth           = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    deactivated    = models.IntegerField(blank=True, default=0)
    username       = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    username_lower = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    password       = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    email          = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    email_verified = models.IntegerField(null=True, blank=True, db_index=True, default=0)
    website        = models.CharField(max_length=255,null=True, blank=True, default='')
    psn            = models.CharField(max_length=255,null = True)
    twitter              = models.CharField(max_length=255,null=True, blank=True, default='')
    twitter_oauth        = models.IntegerField(null=True, blank=True, default=0)
    twitter_oauth_key    = models.CharField(max_length=255,null = True)
    twitter_oauth_secret = models.CharField(max_length=255,null = True)
    twitter_oauth_string = models.CharField(max_length=255,null = True)
    twitter_sync         = models.IntegerField(null=True, blank=True, default=0)
    twitter_id           = models.IntegerField(null = True, blank = True)
    twitter_name         = models.CharField(max_length=255,null = True)
    twitter_screen_name  = models.CharField(max_length=255,null = True)
    twitter_location     = models.CharField(max_length=255,null = True)
    twitter_description  = models.TextField(null = True, blank = True)
    twitter_profile_image_url = models.CharField(max_length=255,null = True)
    twitter_url               = models.CharField(max_length=255,null = True)
    twitter_statuses_count    = models.IntegerField(null = True, blank = True)
    twitter_followers_count   = models.IntegerField(null = True, blank = True)
    twitter_friends_count     = models.IntegerField(null = True, blank = True)
    twitter_favourites_count  = models.IntegerField(null = True, blank = True)
    use_my_css = models.IntegerField(null=True, blank=True, default=0)
    my_css     = models.TextField(null=True, blank=True, default='')
    my_home    = models.CharField(max_length=255,null=True, blank=True, default='')
    location   = models.CharField(max_length=255,null=True, blank=True, default='')
    tagline    = models.TextField(null=True, blank=True, default='')
    bio        = models.TextField(null=True, blank=True, default='')
    avatar_large_url  = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    avatar_normal_url = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    avatar_mini_url   = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_signin   = models.DateTimeField(default = timezone.now)
    blocked       = models.TextField(null=True, blank=True, default='')
    l10n          = models.CharField(max_length=8,default='en')
    favorited_nodes   = models.IntegerField(blank=True, default=0)
    favorited_topics  = models.IntegerField(blank=True, default=0)
    favorited_members = models.IntegerField(blank=True, default=0)
    followers_count   = models.IntegerField(blank=True, default=0)
    level         = models.IntegerField(blank=True, default=1000)
    notifications = models.IntegerField(blank=True, default=0)
    notification_position = models.IntegerField(blank=True, default=0)
    private_token         = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    ua              = models.CharField(max_length=255,null=True, blank=True, default='')
    newbie          = models.IntegerField(blank=True, default=0)
    noob            = models.IntegerField(blank=True, default=0)
    show_home_top   = models.IntegerField(blank=True, default=1)
    show_quick_post = models.IntegerField(blank=True, default=0)
    btc    = models.CharField(max_length=255,null=True, blank=True, default='')
    github = models.CharField(max_length=255,null=True, blank=True, default='')

    def __unicode__(self):
        return self.username

    @property
    def username_lower_md5(self):
        return hashlib.md5(self.username_lower).hexdigest()

    @property
    def created_ts(self):
        a=self.created
        return self.created.strftime("%S")

    def hasFavorited(self, something):
        if type(something).__name__ == 'Node':
            n = 'r/n' + str(something.num) + '/m' + str(self.num)
            r = cache.get(n)
            if r:
                return r
            else:
                #q = models.GqlQuery("SELECT * FROM NodeBookmark WHERE node =:1 AND member = :2", something, self)
                q = NodeBookmark.objects.filter(node = something, member = self)
                if q.count() > 0:
                    cache.set(n, True, 86400 * 14)
                    return True
                else:
                    cache.set(n, False, 86400 * 14)
                    return False
        else:
            if type(something).__name__ == 'Topic':
                n = 'r/t' + str(something.num) + '/m' + str(self.num)
                r = cache.get(n)
                if r:
                    return r
                else:
                    #q = models.GqlQuery("SELECT * FROM TopicBookmark WHERE topic =:1 AND member = :2", something, self)
                    q = TopicBookmark.objects.filter(topic = something, member = self)
                    if q.count() > 0:
                        cache.set(n, True, 86400 * 14)
                        return True
                    else:
                        cache.set(n, False, 86400 * 14)
                        return False
            else:
                if type(something).__name__ == 'Member':
                    n = 'r/m' + str(something.num) + '/m' + str(self.num)
                    r = cache.get(n)
                    if r:
                        return r
                    else:
                        #q = models.GqlQuery("SELECT * FROM MemberBookmark WHERE one =:1 AND member_num = :2", something, self.num)
                        q = MemberBookmark.objects.filter(one = something, member_num = self.num)
                        if q.count() > 0:
                            cache.set(n, True, 86400 * 14)
                            return True
                        else:
                            cache.set(n, False, 86400 * 14)
                            return False
                else:
                    return False

class Counter(models.Model):
    name    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    value   = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    last_increased = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

class Section(models.Model):
    num   = models.IntegerField(db_index=True)
    name  = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title_alternative = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    header        = models.TextField(null = True, blank = True)
    footer        = models.TextField(null = True, blank = True)
    nodes         = models.IntegerField(default=0)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

class Node(models.Model):
    num         = models.IntegerField(db_index=True)
    section_num = models.IntegerField(db_index=True)
    name        = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title       = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title_alternative = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    header      = models.TextField(null = True, blank=True)
    footer      = models.TextField(null = True, blank=True)
    sidebar     = models.TextField(null = True, blank=True)
    sidebar_ads = models.TextField(null = True, blank=True)
    category    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    topics      = models.IntegerField(default=0)
    parent_node_name  = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    avatar_large_url  = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    avatar_normal_url = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    avatar_mini_url   = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

class Topic(models.Model):
    num        = models.IntegerField(db_index=True)
    node       = models.ForeignKey(Node)
    node_num   = models.IntegerField(db_index=True)
    node_name  = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    node_title = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    member     = models.ForeignKey(Member)
    member_num = models.IntegerField(db_index=True)
    title            = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    content          = models.TextField(null = True, blank=True)
    content_rendered = models.TextField(null = True, blank=True)
    content_length   = models.IntegerField(blank=True, default=0)
    has_content   = models.BooleanField(blank=True, default=True)
    hits          = models.IntegerField(default=0)
    stars         = models.IntegerField(blank=True, default=0)
    replies       = models.IntegerField(default=0)
    created_by    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    last_reply_by = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    source        = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    type          = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    type_color    = models.CharField(max_length=8,null = True)
    explicit      = models.IntegerField(blank=True, default=0)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_touched  = models.DateTimeField()

    def __unicode__(self):
        return self.title

class Reply(models.Model):
    num           = models.IntegerField(db_index=True)
    topic         = models.ForeignKey(Topic)
    topic_num     = models.IntegerField(db_index=True)
    member        = models.ForeignKey(Member)
    member_num    = models.IntegerField(db_index=True)
    content       = models.TextField(null = True, blank = True)
    source        = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    created_by    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    highlighted   = models.IntegerField(blank=True, default=0)

class Avatar(models.Model):
    num     = models.IntegerField(db_index=True)
    name    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    content = models.ImageField(upload_to='avatars/',max_length=255)

class Note(models.Model):
    num        = models.IntegerField(db_index=True)
    member     = models.ForeignKey(Member)
    member_num = models.IntegerField(db_index=True)
    title      = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    content    = models.TextField(null = True, blank = True)
    body       = models.TextField(null = True, blank = True)
    length     = models.IntegerField(db_index=False, default=0)
    edits      = models.IntegerField(db_index=False, default=1)
    created    = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class PasswordResetToken(models.Model):
    token     = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    email     = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    member    = models.ForeignKey(Member)
    valid     = models.IntegerField(null=True, blank=True, db_index=True, default=1)
    timestamp = models.IntegerField(null=True, blank=True, db_index=True, default=0)

class Place(models.Model):
    num           = models.IntegerField(null=True, blank=True, db_index=True)
    ip            = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    name          = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    visitors      = models.IntegerField(null=True, blank=True, default=0, db_index=True)
    longitude     = models.FloatField(null=True, blank=True, default=0.0, db_index=True)
    latitude      = models.FloatField(null=True, blank=True, default=0.0, db_index=True)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class PlaceMessage(models.Model):
    num       = models.IntegerField(db_index=True)
    place     = models.ForeignKey(Place)
    place_num = models.IntegerField(db_index=True)
    member    = models.ForeignKey(Member)
    content   = models.TextField(null = True, blank = True)
    in_reply_to = models.ForeignKey('self',null=True,blank=True)
    source    = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    created   = models.DateTimeField(auto_now_add=True)

class Checkin(models.Model):
    place           = models.ForeignKey(Place)
    member          = models.ForeignKey(Member)
    last_checked_in = models.DateTimeField(auto_now=True)

class Site(models.Model):
    num         = models.IntegerField(null=True, blank=True, db_index=True)
    title       = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    slogan      = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    description = models.TextField(null = True, blank = True)
    domain      = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    analytics   = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    home_categories = models.TextField(null=True, blank=True, db_index=False)
    meta            = models.TextField(null=True, blank=True, default='')
    home_top        = models.TextField(null=True, blank=True, default='')
    theme           = models.CharField(max_length=255,null=True, blank=True, default='default')
    l10n            = models.CharField(max_length=8,default='en')
    use_topic_types = models.BooleanField(default=False)
    topic_types     = models.TextField(default='')
    topic_view_level    = models.IntegerField(blank=True, default=-1)
    topic_create_level  = models.IntegerField(blank=True, default=1000)
    topic_reply_level   = models.IntegerField(blank=True, default=1000)
    data_migration_mode = models.IntegerField(blank=True, default=0)

class Minisite(models.Model):
    num           = models.IntegerField(null=True, blank=True, db_index=True)
    name          = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title         = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    description   = models.TextField(default='')
    pages         = models.IntegerField(default=0)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Page(models.Model):
    num      = models.IntegerField(null=True, blank=True, db_index=True)
    name     = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    title    = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    minisite = models.ForeignKey(Minisite)
    content  = models.TextField(default='')
    content_rendered = models.TextField(default='')
    content_type     = models.CharField(max_length=20,default='text/html')
    weight  = models.IntegerField(blank=True, default=0)
    mode    = models.IntegerField(blank=True, default=0)
    hits    = models.IntegerField(blank=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class NodeBookmark(models.Model):
    node    = models.ForeignKey(Node, db_index=True)
    member  = models.ForeignKey(Member, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

class TopicBookmark(models.Model):
    topic   = models.ForeignKey(Topic, db_index=True)
    member  = models.ForeignKey(Member, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

class MemberBookmark(models.Model):
    one        = models.ForeignKey(Member, db_index=True)
    member_num = models.IntegerField(db_index=True)
    created    = models.DateTimeField(auto_now_add=True)

# Notification type: mention_topic, mention_reply, reply
class Notification(models.Model):
    num            = models.IntegerField(null=True, blank=True, db_index=True)
    member         = models.ForeignKey(Member, db_index=True)
    for_member_num = models.IntegerField(null=True, blank=True, db_index=True)
    type           = models.CharField(max_length=255,null=True, blank=True, db_index=True)
    payload        = models.TextField(null=True, blank=True, default='')
    label1         = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    link1          = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    label2         = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    link2          = models.CharField(max_length=255,null=True, blank=True, db_index=False)
    created        = models.DateTimeField(auto_now_add=True)

class Item(models.Model):
    title         = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    description   = models.TextField(null=True, blank=True, default='')
    price         = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    category      = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='gadgets')
    column        = models.IntegerField(null=True, blank=True, default=1, db_index=True)
    link_official = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    link_picture  = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    link_buy      = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    node_name     = models.CharField(max_length=255,null=True, blank=True, db_index=False, default='')
    published     = models.IntegerField(null=True, blank=True, default=0, db_index=True)
    created       = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)