from django.contrib import admin
from .models import Member,Counter,MemberBookmark,Section,Node,Site,Topic,Reply,Avatar,Notification

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name','title','category')
    list_filter = ('category',)
    search_fields = ['title']
#	raw_id_fields = ('question', )

#class AnswerAdmin(admin.ModelAdmin):
#	#list_display = ('summary',)
#	#list_filter = ('status', 'priority')
#	raw_id_fields = ('question', )

admin.site.register(Member)
admin.site.register(MemberBookmark)
admin.site.register(Counter)
admin.site.register(Node, NodeAdmin)
admin.site.register(Section)
admin.site.register(Site)
admin.site.register(Topic)
admin.site.register(Reply)
admin.site.register(Avatar)
admin.site.register(Notification)