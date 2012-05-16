#!/usr/bin/env python
import urllib

import webapp2
import jinja2
import os
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


from google.appengine.ext import db

class File(db.Model):
    name = db.StringProperty(multiline=False)
    type = db.StringProperty(multiline=False)
    iv = db.StringProperty(multiline=False)
    blob = blobstore.BlobReferenceProperty()

    
class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.out.write(
            template.render({
                'files': (db.GqlQuery("SELECT * "
                                      "FROM File")),
                'upload_url': blobstore.create_upload_url('/upload')
            })
        )


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        #print('UploadHandler' + self.request.params['iv'])
        # TODO handle multiple file uploads
        upload = self.get_uploads()[0]
        file = File()
        file.name = self.request.params['name']
        file.type = self.request.params['type']
        file.iv = self.request.params['iv']
        file.blob = upload.key()
        file.put()
        self.redirect('/')


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/upload', UploadHandler),
    ('/download/([^/]+)?', DownloadHandler)
], debug=True)
