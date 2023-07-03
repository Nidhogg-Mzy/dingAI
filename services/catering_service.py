from typing import List
import re
import requests
import datetime
import json
import configparser
from base_service import BaseService


class CateringService(BaseService):
    date_pattern = re.compile(r"\b\d{2}-\d{2}\b")
    url = ''

    @staticmethod
    def load_config(configs: dict) -> None:
        CateringService.url = configs.get('ust', 'catering_url')

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        if len(query) == 0:
            raise ValueError('Invalid query: query length is 0, but is passed into CateringService')
        if query[0] not in ['cater', 'catering', 'Cater']:
            raise ValueError(f'Invalid query: query[0] = "{query[0]}", but is passed into CateringService')
        if len(query) > 1 and query[1] == 'help':
            return CateringService.get_help()
        if len(query) < 1 and not re.search(CateringService.date_pattern, query[1]):
            return 'please provide date in XX-XX format'
        if len(query) == 1:
            return CateringService.get_data(datetime.date.today().strftime("%m-%d"))
        else:
            return CateringService.get_data(query[1])

    @staticmethod
    def get_help() -> str:
        return ''

    @staticmethod
    def format_date(date):
        date = date.split('-')
        month = date[0].lstrip('0')
        day = date[1].lstrip('0')
        return f'{month}-{day}'

    @staticmethod
    def get_data(date):
        url = f"http://localhost:60001/catering/{CateringService.format_date(date)}"
        payload = {}
        headers = {}
        response = json.loads(requests.request("GET", url, headers=headers, data=payload, timeout=20).text)
        return_val = ''
        for keys, values, in response.items():
            return_val += f'- {keys}: {values}\n'
        return return_val


if __name__ == '__main__':
    print(CateringService.process_query(['catering'], user_id='aksdng'))
