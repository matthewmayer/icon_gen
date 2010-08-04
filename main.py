import cgi
import datetime
import logging
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

logging.getLogger().setLevel(logging.DEBUG)


class IconSet(db.Model):
    iphone4_app = db.BlobProperty()
    iphone_app = db.BlobProperty()
    ipad_app = db.BlobProperty()
    
    iphone4_spot = db.BlobProperty()
    iphone_spot = db.BlobProperty()
    ipad_spot = db.BlobProperty()
    
    appstore = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""<html><body>
              <h1>iPhone Icon Generator</h1>
              <p>Provide a 512x512 PNG-format icon image and we'll create the rest.</p>
              <form action="/generate" enctype="multipart/form-data" method="post">
                <div><label>Icon File:</label><input type="file" name="img"/></div>
                <div><input type="submit" value="Generate Icons"></div>
              </form>
            </body>
          </html>""")




class Image (webapp.RequestHandler):
    def get(self):
        iconset = db.get(self.request.get("img_id"))
        img_type = self.request.get("type")
        img = getattr(iconset, img_type)
        self.response.headers['Content-Type'] = "image/png"
        
        if img:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(img)
        else:
            self.response.out.write("No image")




class Generate(webapp.RequestHandler):
    
    def resize(self, w, h):
        return images.resize(self.request.get("img"), w, h)
    
    def post(self):

        icon_types = [
            {'section':'Application icons'},
            {'type':'iphone_app' 	,'name':'iPhone'		,'size':57	,'filename':'Icon.png'},
            {'type':'iphone4_app' 	,'name':'iPhone 4'		,'size':114	,'filename':'Icon@2x.png'},
            {'type':'ipad_app' 		,'name':'iPad'			,'size':72	,'filename':'Icon-72.png'},
            {'section':'Search/settings icons'},
            {'type':'iphone_spot' 	,'name':'Spotlight iPhone'	,'size':29	,'filename':'Icon-Small.png'},
            {'type':'iphone4_spot' 	,'name':'Spotlight iPhone 4'	,'size':58	,'filename':'Icon-Small@2x.png'},
            {'type':'ipad_spot' 	,'name':'Spotlight iPad'	,'size':50	,'filename':'Icon-Small-50.png'},
            {'section':'Original'},
            {'type':'appstore' 		,'name':'Original' 		,'size':512	,'filename':'Original512.png'},
	 ]



        g = IconSet()
        g.put()     
           
        images = []
        for genre in icon_types:
            if 'section' in genre:
                images.append(genre)
            else:
                img = self.request.get("img")
                size = genre['size']		
                if (size<512):
                    img = db.Blob(self.resize(size,size))
                else:
                    img = db.Blob(img)
                setattr(g,genre['type'],img)
                images.append(genre)
        g.put()	
        path = os.path.join(os.path.dirname(__file__), 'templates','generate.html')
        self.response.out.write(template.render(path, {"images":images, "img_id":g.key()}))



application = webapp.WSGIApplication([
    ('/', MainPage)
    ,('/img/.*', Image)
    ,('/generate', Generate)
], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
