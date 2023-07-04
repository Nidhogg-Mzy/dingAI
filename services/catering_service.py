from json import JSONDecodeError
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
        if len(query) > 1 and query[1] == 'help':
            return CateringService.get_help()
        if len(query) == 1:
            return CateringService.get_data('today')
        else:
            return CateringService.get_data(query[1])

    @staticmethod
    def get_help() -> str:
        return '**CateringService is a service that uses HKUST catering API to provide the precise open time of each catering facility.** \n\n ' \
               '**[Basic Usage]** \n ' \
               '- *catering/cater/Cater* [date]: get the open time of the catering facilities in HKUST on the specific date.\n' \
               '- *catering/cater/Cater* today: get today\'s open time of the catering facilities in HKUST.\n' \
               '- *catering/cater/Cater* tmr/tomorrow: get tomorrow\'s open time of the catering facilities in HKUST.\n' \


    @staticmethod
    def get_data(date):
        url = f"{CateringService.url}{date}"
        response = requests.request("GET", url, timeout=20)
        print(response.text)
        if response.status_code == 200:
            return_val = ''
            for keys, values, in json.loads(response.text).items():
                return_val += f'- {keys}: {values}\n'
            return return_val
        else:
            try:
                return json.loads(response.text)['error']
            except (KeyError, JSONDecodeError):
                return 'Unknown Error: ' + response.text


if __name__ == '__main__':
    CateringService.url = 'http://localhost:60001/catering/'
    print(CateringService.process_query(['catering', '88/888888'], user_id='qlrj2'))
