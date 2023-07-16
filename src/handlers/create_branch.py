import json

from pydantic import ValidationError

from src.shared.database.branch_db import BranchDB
from src.shared.dtos.create_branch_dto import CreateBranchDTO
from src.shared.services.schedule_scraper_service import ScheduleScraperService


def handler(event, context):
    event_body = json.loads(event.get('body') or '{}')

    try:
        branch_params = CreateBranchDTO(**event_body)
    except ValidationError:
        return {
            'statusCode': 400
        }

    branch_db = BranchDB()

    if branch_db.branch_data_exists(branch_params.branch_id):
        return {
            'statusCode': 409
        }

    scraper_service = ScheduleScraperService()

    try:
        if branch_params.branch_id == 'base':
            branch_data = scraper_service.fetch_base_branch_data()
        else:
            branch_data = scraper_service.fetch_branch_data(
                branch_id=branch_params.branch_id,
                branch_link=branch_params.branch_link,
                branch_type=branch_params.branch_type
            )
    except Exception as e:
        print('Could not connect to source server:', e)
        return {
            'statusCode': 503
        }

    if branch_data is None:
        return {
            'statusCode': 404
        }

    try:
        branch_db.put_branch_data(
            branch_id=branch_params.branch_id,
            branch_data=branch_data
        )
    except Exception as e:
        print(f'Could not put the data for {branch_params.branch_id} in db:', e)
        return {
            'statusCode': 403
        }

    parsed_data = [data.model_dump() for data in branch_data]

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': parsed_data
        })
    }
