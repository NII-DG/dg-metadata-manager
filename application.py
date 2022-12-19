from flask.app import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)

manager = Manager(app)
app.config.from_pyfile("config/base_setting.py")

# linux export ops_config=local|production
# windows set ops_config=local|production
if "ops_config" in os.environ:
    print("Overide Config")
    app.config.from_pyfile("config/%s_setting.py" % (os.environ['ops_config']))

# config 確認
print("=========================================================================")
print(app.config)
print("=========================================================================")
# print(os.environ)
print("=========================================================================")

db = SQLAlchemy(app)
