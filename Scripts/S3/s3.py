import socket

import boto
import os
from boto.s3.key import Key
from botocore.compat import file_type


from Scripts import KeyLoader

keys = KeyLoader.KeyLoader('../../keys.json')
awsID, aws_secret = keys.getCredentials('aws')


os.environ['AWS_APP_ID'] = awsID
os.environ['AWS_APP_SECRET'] = aws_secret

conn = boto.connect_s3(
        aws_access_key_id = awsID,
        aws_secret_access_key = aws_secret,
        )
for bucket in conn.get_all_buckets():
        print("{name}\t{created}".format(
                name = bucket.name,
                created = bucket.creation_date,
        ))
testfile = 'result.csv'

bucket1 = conn.get_bucket("elasticbeanstalk-us-east-1-081891355789")

k = Key(bucket1)
k.key = 'PlezaDump'

k.set_contents_from_filename('result.csv', policy='public-read')
