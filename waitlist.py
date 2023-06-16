import json
from configparser import ConfigParser
import requests

config = ConfigParser()
config.read('config.ini')
URL = config['waitlist']['url']

payload = {}


def get_header(qq: str) -> dict:
    """
    get header from qq account
    """
    all_configs = None
    with open("test.config", "r", encoding="utf-8") as f:
        all_configs = json.load(f)
    return {} if qq not in all_configs else \
        {
            'Authorization': f'Bearer {all_configs[qq]}',
            'Cookie': 'language=en-US'
        }


if __name__ == '__main__':
    headers = get_header("3429582673")

    response = requests.request("GET", URL, headers=headers, data=payload, timeout=20)

    json_response = json.loads(response.text)
    stdInfo = json_response['stdtInfo'][0]
    waitList = stdInfo['studentClassWaitlist']
    INFO = ''
    for c in waitList:
        INFO += f'course code: {c["crseCode"]}, waitlist position: {c["waitPosition"]}\n'

    print(INFO)
