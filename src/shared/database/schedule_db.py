from typing import Optional

import boto3


class ScheduleDB:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'ath-schedule-cache'

    def schedule_body_exists(self, schedule_id: str) -> bool:
        try:
            self.s3.head_object(
                Bucket=self.bucket,
                Key=f'{schedule_id}.ics'
            )
        except Exception as e:
            print(f'Could not head object {schedule_id}.ics:', e)
            return False

        return True

    def get_schedule_body(self, schedule_key: str) -> Optional[str]:
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=f'{schedule_key}.ics'
            )
        except Exception as e:
            print(f'Could not get object {schedule_key}.ics:', e)
            return None

        return response.get('Body').read().decode('utf-8')

    def put_schedule_body(self, schedule_key: str, schedule_body: str) -> bool:
        try:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=f'{schedule_key}.ics',
                Body=schedule_body
            )
        except Exception as e:
            print(f'Could not put object for {schedule_key} to s3:', e)
            return False

        return True
