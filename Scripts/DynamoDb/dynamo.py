from boto import dynamodb
from boto import dynamodb2
from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.table import Table
from Scripts import KeyLoader
import os
from boto.dynamodb2.items import Item
from flask import (
    _app_ctx_stack as stack,
)


keys = KeyLoader.KeyLoader('../../keys.json')
awsID, aws_secret = keys.getCredentials('aws')


os.environ['AWS_APP_ID'] = awsID
os.environ['AWS_APP_SECRET'] = aws_secret



conn = dynamodb.connect_to_region(
        'us-east-1',
        aws_access_key_id= awsID,
        aws_secret_access_key= aws_secret)
print (conn.list_tables())



usr = Table('User_Sentiment')
conn.usr.put_item(
    Item={
        'User_ID': '123',
        'Concept': 'happy',
        'Score': '10',
        'Sentiment': 'positive'
    })




