from typing import Optional

import boto3


class ScheduleDB:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def schedule_body_exists(self, schedule_id: str) -> bool:
        try:
            self.s3.head_object(Bucket='ath-schedule-cache', Key=f'{schedule_id}.ics')
        except Exception as e:
            print(f'Could not head object {schedule_id}.ics:', e)
            return False

        return True

    def get_schedule_body(self, schedule_id: str) -> Optional[str]:
        try:
            response = self.s3.get_object(Bucket='ath-schedule-cache', Key=f'{schedule_id}.ics')
        except Exception as e:
            print(f'Could not get object {schedule_id}.ics:', e)
            return None

        return response.get('Body').read().decode('utf-8')
