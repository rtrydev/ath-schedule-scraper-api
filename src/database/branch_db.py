import datetime
import json
from typing import List, Union

import boto3

from src.models.feed_item import FeedItem
from src.models.schedule_item import ScheduleItem


class BranchDB:
    def __init__(self):
        self.dynamo_db = boto3.client('dynamodb')
        self.table = 'ath-schedule-branches'

    def get_branch_data(self, branch_id: str) -> Union[List[FeedItem], List[ScheduleItem]]:
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key={
                'branch_id': {
                    'S': branch_id
                }
            }
        )

        branch_data = json.loads(
            response.get('Item', {}).get('branch_data', {}).get('S')
        )

        return [
            FeedItem(
                type=branch_item.get('type'),
                branch=branch_item.get('branch'),
                link=branch_item.get('link'),
                title=branch_item.get('title')
            )
            if branch_item.get('link') is not None
            else ScheduleItem(
                id=branch_item.get('id'),
                type=branch_item.get('type'),
                title=branch_item.get('title')
            )
            for branch_item in branch_data
        ]

    def branch_data_exists(self, branch_id: str) -> bool:
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key={
                'branch_id': {
                    'S': branch_id
                }
            }
        )

        item = response.get('Item', {}).get('branch_data', {}).get('S')

        return item is not None

    def put_branch_data(self, branch_id: str, branch_data: Union[List[FeedItem], List[ScheduleItem]]):
        ttl_timestamp = int((datetime.datetime.now() + datetime.timedelta(days=3)).timestamp())

        dumped_data = json.dumps(
            [
                branch_item.model_dump()
                for branch_item in branch_data
            ]
        )

        self.dynamo_db.put_item(
            TableName=self.table,
            Item={
                'branch_id': {
                    'S': branch_id
                },
                'branch_data': {
                    'S': dumped_data
                },
                'ttl': {
                    'N': str(ttl_timestamp)
                }
            }
        )
