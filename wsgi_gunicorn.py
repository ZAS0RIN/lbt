from werkzeug.contrib.fixers import ProxyFix
from app import app
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=900)
