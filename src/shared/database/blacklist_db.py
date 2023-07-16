import datetime

import boto3


class BlacklistDB:
    def __init__(self):
        self.dynamo_db = boto3.client('dynamodb')
        self.table = 'ath-schedule-blacklist'

    def is_blacklisted(self, item_id: str):
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key={
                'id': {
                    'S': item_id
                }
            }
        )

        return response.get('Item') is not None

    def put_blacklist(self, item_id: str):
        ttl_timestamp = int((datetime.datetime.now() + datetime.timedelta(days=3)).timestamp())

        self.dynamo_db.put_item(
            TableName=self.table,
            Item={
                'id': {
                    'S': item_id
                },
                'ttl': {
                    'N': str(ttl_timestamp)
                }
            }
        )
