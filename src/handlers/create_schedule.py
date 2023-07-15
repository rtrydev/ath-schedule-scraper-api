import json

from pydantic import ValidationError

from src.shared.database.schedule_db import ScheduleDB
from src.shared.dtos.create_schedule_dto import CreateScheduleDTO
from src.shared.services.ics_parser_service import ICSParserService
from src.shared.services.schedule_scraper_service import ScheduleScraperService


def handler(event, context):
    event_body = json.loads(event.get('body') or '{}')

    try:
        schedule_params = CreateScheduleDTO(**event_body)
    except ValidationError:
        return {
            'statusCode': 400
        }

    schedule_key = f'{schedule_params.schedule_id}-{schedule_params.week}'

    schedule_db = ScheduleDB()
    schedule_exists = schedule_db.schedule_body_exists(schedule_key)

    if schedule_exists:
        return {
            'statusCode': 409
        }

    scraper_service = ScheduleScraperService()

    try:
        schedule_data = scraper_service.fetch_ics_schedule_file(
            schedule_id=schedule_params.schedule_id,
            schedule_type=schedule_params.schedule_type,
            week=schedule_params.week
        )
    except Exception as e:
        print('Source server connection failed:', e)
        return {
            'statusCode': 503
        }

    if schedule_data is None:
        return {
            'statusCode': 404
        }

    ics_parser = ICSParserService()

    try:
        parsed_schedule = ics_parser.parse_ics_to_json(schedule_data)
    except Exception as e:
        print(f'Could not parse the schedule {schedule_key}.ics', e)
        return {
            'statusCode': 422
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': parsed_schedule
        })
    }
