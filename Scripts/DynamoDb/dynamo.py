from boto import dynamodb
from boto import dynamodb2
from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.table import Table
from Scripts import KeyLoader
from boto.dynamodb2.items import Item
from flask import (
    _app_ctx_stack as stack,
)


keys = KeyLoader.KeyLoader('../../keys.json')

awdbID, awdbSecret = keys.getCredentials('aws_dynamo')
DEFAULT_REGION = 'us-east-1'


# conn = dynamodb.connect_to_region(
#         'us-east-1',
#         aws_access_key_id= awdbID,
#         aws_secret_access_key= awdbSecret)
# print (conn.list_tables())
#


# dynamodb2.table.put_item(
#     Item={
#         'User_ID': '123',
#         'Concept': 'happy',
#         'Score': '10',
#         'Sentiment': 'positive'
#     })


class ConfigurationError(Exception):
    pass


class Dynammo(object):
    def __init__(self, app=None):
        """
        Initialize this extension.
        :param obj app: The Flask application (optional).
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize this extension.
        :param obj app: The Flask application.
        """
        self.app = app
        self.init_settings()
        self.check_settings()

    def init_settings(self):
        """Initialize all of the extension settings."""
        self.default('AWS_ACCESS_KEY_ID', awdbID)
        self.default('AWS_SECRET_ACCESS_KEY', awdbSecret)
        self.default('DYNAMO_TABLES', [])
        self.default('AWS_REGION', DEFAULT_REGION)

    def connection(self):
        # """
        # Our DynamoDB connection.
        # This will be lazily created if this is the first time this is being
        # accessed.  This connection is reused for performance.
        # """
        # ctx = stack.top
        # if ctx is not None:
        #     if not hasattr(ctx, 'dynamo_connection'):
        #         kwargs = {
        #             'host': self.app.config['DYNAMO_LOCAL_HOST'] if self.app.config['DYNAMO_ENABLE_LOCAL'] else None,
        #             'port': int(self.app.config['DYNAMO_LOCAL_PORT']) if self.app.config[
        #                 'DYNAMO_ENABLE_LOCAL'] else None,
        #             'is_secure': False if self.app.config['DYNAMO_ENABLE_LOCAL'] else True,
        #         }
        #
        #         # Only apply if manually specified: otherwise, we'll let boto
        #         # figure it out (boto will sniff for ec2 instance profile
        #         # credentials).
        #         if self.app.config['AWS_ACCESS_KEY_ID']:
        #             kwargs['aws_access_key_id'] = self.app.config['AWS_ACCESS_KEY_ID']
        #         if self.app.config['AWS_SECRET_ACCESS_KEY']:
        #             kwargs['aws_secret_access_key'] = self.app.config['AWS_SECRET_ACCESS_KEY']
        #
        #         # If DynamoDB local is disabled, we'll remove these settings.
        #         if not kwargs['host']:
        #             del kwargs['host']
        #         if not kwargs['port']:
        #             del kwargs['port']

        dynamo_connection = dynamodb.connect_to_region('us-east-1',aws_access_key_id= awdbID,aws_secret_access_key= awdbSecret)
        #dynamo_connection.list_tables()
        return dynamo_connection

    def check_settings(self):
        """
        Check all user-specified settings to ensure they're correct.
        We'll raise an error if something isn't configured properly.
        :raises: ConfigurationError
        """
        if self.app.config['AWS_ACCESS_KEY_ID'] and not self.app.config['AWS_SECRET_ACCESS_KEY']:
            raise ConfigurationError('You must specify AWS_SECRET_ACCESS_KEY if you are specifying AWS_ACCESS_KEY_ID.')

        if self.app.config['AWS_SECRET_ACCESS_KEY'] and not self.app.config['AWS_ACCESS_KEY_ID']:
            raise ConfigurationError('You must specify AWS_ACCESS_KEY_ID if you are specifying AWS_SECRET_ACCESS_KEY.')

        if self.app.config['DYNAMO_ENABLE_LOCAL'] and not (
            self.app.config['DYNAMO_LOCAL_HOST'] and self.app.config['DYNAMO_LOCAL_PORT']):
            raise ConfigurationError('If you have enabled Dynamo local, you must specify the host and port.')



    def add_item(self,table):
        if table == 'User_Sentiment':
            tableData = self.user_item()
            table.put_item(tableData)

            print(tableData)

        # else if table == 'User_Meta':
        #     print(table)
        #     table.cumulative_item()
        # else if table == 'User_Cumulative':
        #     print(table)
        #     table.meta_item()

    def user_item(self):
        data = {
            'User_ID': '123',
            'Concept': 'happy',
            'Score': '10',
            'Sentiment': 'positive'
        }
        return data
    def cumulative_item(self):
        return
        data = {'User_ID': '456',
        'Cconcept': 'good',
        'Cscore': '10',
        'Csentiment': 'ok'
        }
    def meta_item(self):
        return
        data = {
        'User_ID': '789'
        }


# if __name__ == '__main__':
#     dym = Dynammo()
#     dym.check_settings()
#     dym.connection()
#     dym.list_tables()
#     dym.add_item(Table('User_Sentiment'))


