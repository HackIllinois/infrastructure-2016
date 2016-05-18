import urllib

from google.appengine.ext.blobstore.blobstore import BlobInfo as blobstore
from google.appengine.ext.webapp import blobstore_handlers

from www.handlers.base import BaseHandler

class ResumeDownloadHandler(BaseHandler, blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blobstore_key):
        # Test for existence if problems arise
        self.send_blob(blobstore_key, content_type="application/pdf")
