from boto import dynamodb
from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.table import Table
from Scripts import KeyLoader

# keys = KeyLoader.KeyLoader('../../keys.json')
#
# awdbID, awdbSecret = keys.getCredentials('aws_dynamo')

conn = dynamodb.connect_to_region(
        'us-west-2',
        aws_access_key_id='',
        aws_secret_access_key='')


print (conn.list_tables())


