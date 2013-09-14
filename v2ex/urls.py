# -*- coding: utf-8 -*-
# ------------------------------------------------------------

# python.
#import datetime
#import urllib
# ------------------------------------------------------------

# django.
from django.conf.urls.defaults import *
from django.core.paginator import Paginator, InvalidPage
from django.views.generic import DetailView, ListView

from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, \
                                        WeekArchiveView, DayArchiveView, TodayArchiveView, \
                                        DateDetailView

# ------------------------------------------------------------

# 3dpart.
#
# ------------------------------------------------------------

# app
from .views.main   import *
from .views.member import *
from .views.blog   import *
from .views.notes  import *
from .views.my     import *
from .views.page   import *
from .views.place  import *
from .views.avatar import *
from .views.topic  import *
from .views.notifications import *
from .views.backstage     import *
from .views.favorite      import *
from .views.t      import *
# ------------------------------------------------------------

# config.
#
# ------------------------------------------------------------
#


urlpatterns = patterns('',



    url(r'^$',          HomeHandler.as_view(), name='v2ex_index'),
    url(r'^signin',   SigninHandler.as_view(), name='signin'),
    url(r'^signup',   SignupHandler.as_view(), name='signup'),
    url(r'^signout', SignoutHandler.as_view(), name='signout'),
    url(r'^forgot',   ForgotHandler.as_view(), name='forgot'),
    
    url(r'^planes/?', PlanesHandler.as_view()),
    url(r'^recent', RecentHandler.as_view()),
#    (r'/ua', UAHandler),

    url(r'^avatar/([0-9]+)/(large|normal|mini)', AvatarHandler.as_view()),
    url(r'^navatar/([0-9]+)/(large|normal|mini)', NodeAvatarHandler.as_view()),
    
    #place
    url('^place/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', PlaceHandler.as_view()),
    url('^remove/place_message/(.*)', PlaceMessageRemoveHandler.as_view()),

#    (r'/reset/([0-9]+)', PasswordResetHandler),
    (r'^go/([a-zA-Z0-9]+)/graph', NodeGraphHandler.as_view()),
    (r'^go/([a-zA-Z0-9]+)', NodeHandler.as_view()),
#    (r'/n/([a-zA-Z0-9]+).json', NodeApiHandler),
#    (r'/q/(.*)', SearchHandler),
#    (r'/_dispatcher', DispatcherHandler),
    url(r'^changes', ChangesHandler.as_view()),
#    (r'/(.*)', RouterHandler),
    
    #blog
    (r'^blog/([a-z0-9A-Z\_\-]+)', BlogHandler.as_view()),
    (r'^entry/([0-9]+)', BlogEntryHandler.as_view()),
    
    
    (r'^member/([a-z0-9A-Z\_\-]+)', MemberHandler.as_view()),
#    (r'^member/([a-z0-9A-Z\_\-]+).json', MemberApiHandler),
    url(r'^settings$', SettingsHandler.as_view()),
#    (r'/settings/password', SettingsPasswordHandler),
    url(r'^settings/avatar', SettingsAvatarHandler.as_view()),
    url(r'^block/(.*)',     MemberBlockHandler.as_view()),
    url(r'^unblock/(.*)', MemberUnblockHandler.as_view()),

    url('^my/nodes',         MyNodesHandler.as_view()),
    url('^my/topics',       MyTopicsHandler.as_view()),
    url('^my/following', MyFollowingHandler.as_view()),
    
    #favorite.py
    url('^favorite/node/([a-zA-Z0-9]+)', FavoriteNodeHandler.as_view()),
    url('^unfavorite/node/([a-zA-Z0-9]+)', UnfavoriteNodeHandler.as_view()),
    url('^favorite/topic/([0-9]+)', FavoriteTopicHandler.as_view()),
    url('^unfavorite/topic/([0-9]+)', UnfavoriteTopicHandler.as_view()),
    url('^follow/([0-9]+)', FollowMemberHandler.as_view()),
    url('^unfollow/([0-9]+)', UnfollowMemberHandler.as_view()),

    url(r'^notes$',                     NotesHomeHandler.as_view()),
    url(r'^notes/new',                  NotesNewHandler.as_view()),
    url(r'^notes/([0-9]+)$',            NotesItemHandler.as_view()),
    url(r'^notes/([0-9]+)/erase', NotesItemEraseHandler.as_view()),
    url(r'^notes/([0-9]+)/edit',   NotesItemEditHandler.as_view()),
    
    url('^notifications/?', NotificationsHandler.as_view()),
    url('^notifications/check/(.+)', NotificationsCheckHandler.as_view()),
    url('^notifications/reply/(.+)', NotificationsReplyHandler.as_view()),
    url('^notifications/topic/(.+)', NotificationsTopicHandler.as_view()),
    url('^n/([a-z0-9]+).xml', NotificationsFeedHandler.as_view()),
    
    # topic
    url('^new/(.*)', NewTopicHandler.as_view()),
    url('^t/([0-9]+)', TopicHandler.as_view()),
    url('^t/([0-9]+).txt', TopicPlainTextHandler.as_view()),
    url('^edit/topic/([0-9]+)', TopicEditHandler.as_view()),
    url('^delete/topic/([0-9]+)', TopicDeleteHandler.as_view()),
    url('^index/topic/([0-9]+)', TopicIndexHandler.as_view()),
    url('^edit/reply/([0-9]+)', ReplyEditHandler.as_view()),
    url('^hit/topic/(.*)', TopicHitHandler.as_view()),
    url('^hit/page/(.*)', PageHitHandler.as_view()),
    
    url('^backstage$', BackstageHomeHandler.as_view()),
    url('^backstage/new/minisite', BackstageNewMinisiteHandler.as_view()),
    url('^backstage/minisite/(.*)', BackstageMinisiteHandler.as_view()),
    url('^backstage/remove/minisite/(.*)', BackstageRemoveMinisiteHandler.as_view()),
    url('^backstage/new/page/(.*)', BackstageNewPageHandler.as_view()),
    url('^backstage/page/(.*)', BackstagePageHandler.as_view()),
    url('^backstage/remove/page/(.*)', BackstageRemovePageHandler.as_view()),
    url('^backstage/new/section', BackstageNewSectionHandler.as_view()),
    url('^backstage/section/(.*)', BackstageSectionHandler.as_view()),
    url('^backstage/new/node/(.*)', BackstageNewNodeHandler.as_view()),
    url('^backstage/node/([a-z0-9A-Z]+)$', BackstageNodeHandler.as_view()),
    url('^backstage/node/([a-z0-9A-Z]+)/avatar', BackstageNodeAvatarHandler.as_view()),
    url('^backstage/remove/reply/(.*)', BackstageRemoveReplyHandler.as_view()),
    url('^backstage/tidy/reply/([0-9]+)', BackstageTidyReplyHandler.as_view()),
    url('^backstage/tidy/topic/([0-9]+)', BackstageTidyTopicHandler.as_view()),
    url('^backstage/deactivate/user/(.*)', BackstageDeactivateUserHandler.as_view()),
    url('^backstage/move/topic/(.*)', BackstageMoveTopicHandler.as_view()),
    url('^backstage/site', BackstageSiteHandler.as_view()),
    url('^backstage/topic', BackstageTopicHandler.as_view()),
    url('^backstage/remove/mc', BackstageRemoveMemcacheHandler.as_view()),
    url('^backstage/member/(.*)', BackstageMemberHandler.as_view()),
    url('^backstage/members', BackstageMembersHandler.as_view()),
    url('^backstage/remove/notification/(.*)', BackstageRemoveNotificationHandler.as_view()),
    
    #page
    url('^about', AboutHandler.as_view()),
    url('^faq', FAQHandler.as_view()),
    url('^mission', MissionHandler.as_view()),
    url('^advertise$', AdvertiseHandler.as_view()),
    url('^advertisers', AdvertisersHandler.as_view()),
    
    #twitter
    url('^twitter/?$', TwitterHomeHandler.as_view()),
    url('^twitter/mentions/?', TwitterMentionsHandler.as_view()),
    url('^twitter/inbox/?', TwitterDMInboxHandler.as_view()),
    url('^twitter/user/([a-zA-Z0-9\_]+)', TwitterUserTimelineHandler.as_view()),
    url('^twitter/link', TwitterLinkHandler.as_view()),
    url('^twitter/unlink', TwitterUnlinkHandler.as_view()),
    url('^twitter/oauth', TwitterCallbackHandler.as_view()),
    url('^twitter/tweet', TwitterTweetHandler.as_view()),
    url('^twitter/api/?', TwitterApiCheatSheetHandler.as_view()),

)

