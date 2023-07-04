from typing import List
import requests
import json
from .base_service import BaseService


class CateringService(BaseService):
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
        else:
            return CateringService.get_data(query[1])

    @staticmethod
    def get_help() -> str:
        return '**CateringService is a service that uses HKUST catering API to provide the precise open time of each catering facility.** \n\n ' \
               '**[Basic Usage]** \n ' \
               '- *catering/cater/Cater* <date>: get the open time of the catering facilities in HKUST on the specific date.\n' \
               '- *catering/cater/Cater* today: get today\'s open time of the catering facilities in HKUST.\n' \
               '- *catering/cater/Cater* tmr/tomorrow: get tomorrow\'s open time of the catering facilities in HKUST.\n' \


    @staticmethod
    def get_data(date):
        url = f"{CateringService.url}{date}"
        response = requests.request("GET", url, timeout=20)
        if response.status_code == 200:
            return_val = ''
            for keys, values, in json.loads(response.text).items():
                return_val += f'- {keys}: {values}\n'
            return return_val
        else:
            return json.loads(response.text)['error']


if __name__ == '__main__':
    print(CateringService.get_help())
