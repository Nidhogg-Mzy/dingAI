import json
import requests

url = "https://w5.ab.ust.hk/msapi/sis/stdt_class_enrl/%7BstdtID%7D"

payload = {}
def get_header(qq: str) -> dict:
  all_configs = None
  with open("test.config", "r") as f:
    all_configs = json.load(f)
  return {} if qq not in all_configs else \
  {
    'Authorization': f'Bearer {all_configs[qq]}',
    'Cookie': 'language=en-US'
  }

if __name__ == '__main__':
  headers = get_header("3429582673")

  response = requests.request("GET", url, headers=headers, data=payload)

  json_response = json.loads(response.text)
  stdInfo = json_response['stdtInfo'][0]
  waitList = stdInfo['studentClassWaitlist']
  info = ''
  for c in waitList:
    info += f'course code: {c["crseCode"]}, waitlist position: {c["waitPosition"]}\n'

  print(info)

