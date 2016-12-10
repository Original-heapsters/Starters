from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

from flask import Flask
from flask.ext.flask import Dynamo

app = Flask(__name__)
app.config['DYNAMO_TABLES'] = [
    Table('users', schema=[HashKey('username')]),
    Table('groups', schema=[HashKey('name')]),
]
