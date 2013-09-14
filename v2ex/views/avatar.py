#!/usr/bin/env python
# coding=utf-8
try:
    import Image
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError('Photologue was unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.')



from django.core.cache import cache
from django.db import models
#from google.appengine.ext.webapp import util
from django import template
from django.views.generic import View, ListView,TemplateView
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render,redirect


from v2ex.babel.models import Avatar

from v2ex.babel.security import *
from v2ex.babel.da import *
        
class AvatarHandler(View):
    def get(self, request, member_num, size):
        avatar = GetKindByName('Avatar', 'avatar_' + str(member_num) + '_' + str(size))
        if avatar:
            #self.response.headers['Content-Type'] = "image/png"
            #self.response.headers['Cache-Control'] = "max-age=172800, public, must-revalidate"
            #self.response.headers['Expires'] = "Sun, 25 Apr 2011 20:00:00 GMT"
            #self.response.out.write(avatar.content)
            
            ###response = HttpResponse()
            ###response['Content-Type']="image/png"
            ###response['Cache-Control'] = "max-age=172800, public, must-revalidate"
            ###response['Expires'] = "Sun, 25 Apr 2015 20:00:00 GMT"
            ###return response
            try:
                with open(avatar.content.path, "rb") as f:
                    return HttpResponse(f.read(), mimetype="image/jpeg")
            except IOError:
                red = Image.new('RGBA', (1, 1), (255,0,0,0))
                response = HttpResponse(mimetype="image/jpeg")
                red.save(response, "JPEG")
                return response
        else:
            #self.redirect('/static/img/avatar_' + str(size) + '.png')
            return redirect('/static/img/avatar_' + str(size) + '.png')
            
class NodeAvatarHandler(View):
    def get(self, request, node_num, size):
        avatar = GetKindByName('Avatar', 'node_' + str(node_num) + '_' + str(size))
        if avatar:
            self.response.headers['Content-Type'] = "image/png"
            self.response.headers['Cache-Control'] = "max-age=172800, public, must-revalidate"
            self.response.headers['Expires'] = "Sun, 25 Apr 2011 20:00:00 GMT"
            self.response.out.write(avatar.content)
        else:
            #self.error(404)
            return Http404()
            
def main():
    application = webapp.WSGIApplication([
    ('/avatar/([0-9]+)/(large|normal|mini)', AvatarHandler),
    ('/navatar/([0-9]+)/(large|normal|mini)', NodeAvatarHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
