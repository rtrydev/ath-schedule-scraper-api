import json
from typing import List

import boto3

from src.shared.models.feed_item import FeedItem


class BranchDB:
    def __init__(self):
        self.dynamo_db = boto3.client('dynamodb')
        self.table = 'ath-schedule-branches'

    def get_branch_data(self, branch_id: str) -> List[FeedItem]:
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

    def put_branch_data(self, branch_id: str, branch_data: List[FeedItem]):
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
                }
            }
        )
