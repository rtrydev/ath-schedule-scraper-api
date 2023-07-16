import datetime
import json

from src.shared.database.schedule_db import ScheduleDB
from src.shared.globals import WEEK_OFFSET
from src.shared.services.ics_parser_service import ICSParserService


def handler(event, context):
    path_parameters = event.get('pathParameters') or {}
    query_parameters = event.get('queryStringParameters') or {}

    schedule_id = path_parameters.get('schedule_id')
    week = int(query_parameters.get('week'))

    if week is None:
        year, week_num, _ = datetime.datetime.now().isocalendar()
        week = (year - 1970) * 52 + week_num - WEEK_OFFSET
        print('week', week)

    schedule_key = f'{schedule_id}-{week}'

    schedule_db = ScheduleDB()
    schedule = schedule_db.get_schedule_body(schedule_key)

    if schedule is None:
        return {
            'statusCode': 404
        }

    ics_parser = ICSParserService()
    parsed_schedule = ics_parser.parse_ics_to_json(schedule, week)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': parsed_schedule
        })
    }
