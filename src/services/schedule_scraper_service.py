import re
from typing import List, Optional, Union

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..models.feed_item import FeedItem
from ..models.schedule_item import ScheduleItem


class ScheduleScraperService:
    def __init__(self):
        self.base_url = 'https://plany.ath.bielsko.pl'

    def fetch_ics_schedule_file(self, schedule_id: str, schedule_type: str, week: int):
        response = requests.get(
            f'{self.base_url}/plan.php?type={schedule_type}&id={schedule_id}&cvsfile=true&w={week}'
        )

        if response.status_code != 200:
            raise Exception(f'Failed to fetch schedule {schedule_id} of type {schedule_type} for week {week}')

        return response.text

    def fetch_branch_data(self, branch_id: str, branch_type: str, branch_link: str):
        response = requests.post(
            f'{self.base_url}/left_menu_feed.php?type={branch_type}&branch={branch_id}&link={branch_link}'
        )

        if response.status_code != 200:
            raise Exception(
                f'Failed to fetch branch data for branch {branch_id} of type {branch_type} with link {branch_link}'
            )

        return self.__parse_branch_data(response.content)

    def fetch_base_branch_data(self):
        response = requests.get(f'{self.base_url}/left_menu.php')

        if response.status_code != 200:
            raise Exception(
                'Failed to fetch base branch data'
            )

        return self.__parse_base_branch_data(response.content)

    def __parse_branch_data(self, html: bytes) -> Optional[Union[List[FeedItem], List[ScheduleItem]]]:
        feed_items: List[FeedItem] = []
        schedule_items: List[ScheduleItem] = []

        soup = BeautifulSoup(html, 'html.parser')
        branch_list = soup.find('ul')

        if branch_list is None:
            return None

        branch_items: List[Tag] = branch_list.find_all('li')

        if branch_items is None or len(branch_items) == 0:
            return None

        for branch_item in branch_items:
            img = branch_item.find('img')

            if img is None:
                continue

            if img.attrs.get('onclick') is not None:
                feed_items.append(self.__get_onclick_params(branch_item))
                continue
            else:
                schedule_items.append(self.__get_href_params(branch_item))

        if len(feed_items) > 0:
            return feed_items

        return schedule_items

    def __parse_base_branch_data(self, html: bytes) -> Optional[List[FeedItem]]:
        feed_items: List[FeedItem] = []

        soup = BeautifulSoup(html, 'html.parser')
        branch_items: List[Tag] = soup.find_all('li')

        if branch_items is None or len(branch_items) == 0:
            return None

        for branch_item in branch_items:
            branch_call_anchor = branch_item.find('a')

            if branch_call_anchor is None:
                continue

            branch_call = branch_call_anchor.attrs.get('onclick') or ''
            branch_call_params = branch_call.replace('branch(', '').replace(')', '').replace('\'', '').split(',')

            feed_items.append(
                FeedItem(
                    type=branch_call_params[0],
                    branch=branch_call_params[1],
                    link=branch_call_params[2],
                    title=re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\- ]', '', branch_call_params[3])
                )
            )

        return feed_items

    def __get_onclick_params(self, branch_item: Tag) -> FeedItem:
        img = branch_item.find('img')
        branch_call = img.attrs.get('onclick') or ''

        branch_call_params = re.sub(r'[^0-9,]', '', branch_call).split(',')
        title = branch_item.get_text().strip()

        return FeedItem(
            title=title,
            branch=branch_call_params[0],
            type=branch_call_params[3],
            link=branch_call_params[4]
        )

    def __get_href_params(self, branch_item: Tag) -> ScheduleItem:
        anchor = branch_item.find('a')
        schedule_fetch_call = anchor.attrs.get('href') or ''

        branch_type = re.findall(r'type=([0-9]+)', schedule_fetch_call)[0]
        branch_id = re.findall(r'id=([0-9]+)', schedule_fetch_call)[0]
        title = anchor.get_text().strip()

        return ScheduleItem(
            id=branch_id,
            type=branch_type,
            title=title
        )
