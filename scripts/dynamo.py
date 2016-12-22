from botocore.exceptions import ClientError
from scripts  import KeyLoader
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import decimal

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class dynamoOps(object):
    def __init__(self, region='us-east-1'):
        self.region=region

    def setup(self):

        keys = KeyLoader.KeyLoader('keys.json')

        id,secret = keys.getCredentials('aws')

        dynamodb = boto3.resource('dynamodb',aws_access_key_id=id,
            aws_secret_access_key=secret, region_name='us-east-1')

        table = dynamodb.Table('Raw_Data')


        return table

    def getUserByID(self, id):

        table = self.setup()
        response = table.scan()
        results = {}

        if id:
            for i in response['Items']:
                if id.lower() in i['Text'].lower():
                    results[i['TimeStamp']] = i['Text']
        else:
            for i in response['Items']:
                results[i['TimeStamp']] = i['Text']

        return results

    def getPositivePosts(self):
        table = self.setup()

        response = table.scan()

        results = {}

        for i in response['Items']:
            if i['Score'] > 50:
                results[i['TimeStamp']] = i['Text']

        return results

    def addEntry(self, Item):
        table = self.setup()

        response = table.put_item(Item=Item)

        print(response)

if __name__ == '__main__':
    dym = dynamoOps()

    dym.getUserByID('Bob')

    Item = {
        'TimeStamp':'2016_1234',
        'Concept':'con',
        'Role':'role',
        'Score':'1',
        'Sentiment':'sent',
        'Text':'text',
        'User_ID':'1234'
    }

    #dym.addEntry(Item)



