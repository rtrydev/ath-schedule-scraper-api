import json

from src.shared.database.branch_db import BranchDB


def handler(event, context):
    path_parameters = event.get('pathParameters') or {}
    branch_id = path_parameters.get('branch_id')

    branch_db = BranchDB()

    try:
        branch_data = branch_db.get_branch_data(branch_id)
    except Exception as e:
        print(f'Could not get branch data for {branch_id}:', e)
        return {
            'statusCode': 404
        }

    parsed_data = [data.model_dump() for data in branch_data]

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': parsed_data
        })
    }
