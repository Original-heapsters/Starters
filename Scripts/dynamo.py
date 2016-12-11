from botocore.exceptions import ClientError
import json
import boto3
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

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('User_Sentiment')

        return table

    def getUserByID(self, id):

        table = self.setup()

        try:
            response = table.get_item(
                Key={
                    'User_ID': id
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])

        if 'Item' in response:

            item = response['Item']
            print("GetItem succeeded:")
            print(json.dumps(item, indent=4, cls=DecimalEncoder))

            return item
        else:
            return None

if __name__ == '__main__':
    dym = dynamoOps()

    dym.getUserByID('1234')



