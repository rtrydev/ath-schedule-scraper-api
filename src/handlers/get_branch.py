import json

from src.shared.database.dummy_db import DummyDb


def handler(event, context):
    dummy_db = DummyDb()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'hello from get branch',
            'db_data': dummy_db.get_data()
        })
    }
