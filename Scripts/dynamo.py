from botocore.exceptions import ClientError
from Scripts import KeyLoader
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

        keys = KeyLoader.KeyLoader('../keys.json')

        id,secret = keys.getCredentials('aws')

        dynamodb = boto3.resource('dynamodb',aws_access_key_id=id,
            aws_secret_access_key=secret, region_name='us-east-1')

        table = dynamodb.Table('Raw_Data')


        return table

    def getUserByID(self, id):

        table = self.setup()

        pe = "User_ID, Concept"


        response = table.scan(
            #fe=Key('year').between(1950, 1959);
            #KeyConditionExpression=Key('TimeStamp').eq('2016')
            ProjectionExpression=pe
        )
        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))

        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ProjectionExpression=pe,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )

            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))

            return response['Items']
        else:
            return None

    def addEntry(self, Item):
        table = self.setup()

        response = table.put_item(Item=Item)

        print(response)

if __name__ == '__main__':
    dym = dynamoOps()

    dym.getUserByID('1234')

    Item = {
        'TimeStamp':'2016_1234',
        'Concept':'con',
        'Role':'role',
        'Score':'1',
        'Sentiment':'sent',
        'Text':'text',
        'User_ID':'1234'
    }

    dym.addEntry(Item)



