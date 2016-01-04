import sae
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, 'site-packages'))

from tumi import app
application = sae.create_wsgi_app(app)