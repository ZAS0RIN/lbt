#!flask/bin/python
from app import app
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app.run(debug = True)

