import json

from pydantic import ValidationError

from src.database.blacklist_db import BlacklistDB
from src.database.schedule_db import ScheduleDB
from src.dtos.create_schedule_dto import CreateScheduleDTO
from src.services.ics_parser_service import ICSParserService
from src.services.schedule_scraper_service import ScheduleScraperService


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
    blacklist_db = BlacklistDB()

    if blacklist_db.is_blacklisted(schedule_key):
        print(f'Attempted to create blacklisted branch {schedule_key}')
        return {
            'statusCode': 404
        }

    if schedule_db.schedule_body_exists(schedule_key):
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
        blacklist_db.put_blacklist(schedule_key)
        return {
            'statusCode': 404
        }

    ics_parser = ICSParserService()

    try:
        parsed_schedule = ics_parser.parse_ics_to_json(schedule_data, int(schedule_params.week))
    except Exception as e:
        print(f'Could not parse the schedule {schedule_key}.ics', e)
        blacklist_db.put_blacklist(schedule_key)
        return {
            'statusCode': 422
        }

    schedule_db.put_schedule_body(schedule_key, schedule_data)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': parsed_schedule
        })
    }
