import json

from src.shared.services.schedule_scraper_service import ScheduleScraperService


def handler(event, context):
    print(event)

    # scraper_service = ScheduleScraperService()
    # branch_data = scraper_service.fetch_branch_data()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'hello from create branch'
        })
    }
