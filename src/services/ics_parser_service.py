import datetime
import re
from typing import List

from src.globals import WEEK_OFFSET, WEEK_LENGTH_SEC


class ICSParserService:
    def parse_ics_to_json(self, ics_body: str, week: int) -> List[dict]:
        raw_events = []
        current_raw_obj = {}

        absolute_week = week + WEEK_OFFSET
        year = 1970 + int(absolute_week / 52)
        year_week = absolute_week % 52

        week_start_timestamp = int(datetime.datetime.fromisocalendar(year, year_week, 1).timestamp())
        week_end_timestamp = week_start_timestamp + WEEK_LENGTH_SEC

        lines = ics_body.split('\n')

        for line in lines:
            if line == 'BEGIN:VEVENT':
                current_raw_obj = {}
                continue

            if line == 'END:VEVENT':
                raw_events.append({**current_raw_obj})

            key, value = line.split(':')

            current_raw_obj[key] = value

        result = []

        for event in raw_events:
            summary = str(event.get('SUMMARY'))

            speakers = self.__get_speakers(summary)
            rooms = self.__get_rooms(summary)

            stripped_summary = summary

            for speaker in speakers:
                stripped_summary = stripped_summary.replace(speaker, '')

            for room in rooms:
                stripped_summary = stripped_summary.replace(room, '')

            stripped_summary = re.sub(r' +', ' ', stripped_summary).strip()
            summary_items = stripped_summary.split(' ')

            result.append({
                'id': str(event['UID']),
                'start_time': self.__get_timestamp_from_date(str(event['DTSTART'])),
                'end_time': self.__get_timestamp_from_date(str(event['DTEND'])),
                'course': ' '.join(summary_items[0:-1]),
                'type': summary_items[-1],
                'speakers': speakers,
                'rooms': rooms
            })

        return [
            item
            for item in result
            if item.get('start_time') > week_start_timestamp
            and item.get('end_time') < week_end_timestamp
        ]

    def __get_timestamp_from_date(self, date_time: str) -> int:
        [date, time] = date_time.split('T')

        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])

        hour = int(time[0:2])
        minute = int(time[2:4])
        second = int(time[4:6])

        timestamp = datetime.datetime(year, month, day, hour, minute, second).timestamp()

        return int(timestamp)

    def __get_rooms(self, summary: str) -> List[str]:
        room_regex = r'([A-Z][0-9]{1,3}[A-Za-z]?)|(Hala sportowa [0-9]\/[0-9])|(nauczanie zdalne)'

        found_rooms = re.findall(room_regex, summary)
        return [room[0] or room[1] or room[2] for room in found_rooms]

    def __get_speakers(self, summary: str) -> List[str]:
        speakers_regex = r'[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]?[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{1,2}'

        return re.findall(speakers_regex, summary)
