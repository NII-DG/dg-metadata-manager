from flask.app import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from api.utils.print_util.print_log import PrintToTerminal
import os
app = Flask(__name__)

manager = Manager(app)
app.config.from_pyfile("config/base_setting.py")

# linux export ops_config=local|production
# windows set ops_config=local|production
if "ops_config" in os.environ:
    env = os.environ['ops_config']
    msg = 'Overide Config. Selected Environment is {env}.'.format(**{
        'env': env
    })
    PrintToTerminal(msg)
    app.config.from_pyfile("config/%s_setting.py" % (env))

db = SQLAlchemy(app)
