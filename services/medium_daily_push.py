import argparse
import configparser
import datetime
import email
import imaplib
from datetime import datetime, timedelta, time
from typing import List
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup

import dingtalk_receive
from services.base_shceduled_service import BaseScheduledService


class MediumService(BaseScheduledService):
    sender = 'noreply@medium.com'
    parser = argparse.ArgumentParser()

    parser.add_argument('--repeat', type=bool, help='specify if the task is repeating')
    parser.add_argument('--cycle', type=str, default=1, help='the cycle of the service, in days')
    parser.add_argument('--start', type=str, help='when should the service start')
    parser.add_argument('--end', type=str, default=None, help='when should the service end')
    args = parser.parse_args()

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        return ''

    @staticmethod
    def scheduler():
        # Create a scheduler
        date_format = "%Y-%m-%d"
        start = datetime.now().date()
        start_date = datetime.strptime(MediumService.args.start, date_format).date()
        if start_date < datetime.now().date():
            start = datetime.now().date() if start_date < datetime.now().date() else start_date
        default_time = time(8, 0, 0)
        combined_datetime = datetime.combine(start, default_time)
        scheduler = BlockingScheduler()

        cycle_interval = 10  # Cycle interval in seconds

        # Schedule the task to run repeatedly
        if MediumService.args.end is not None:
            scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval, start_date=combined_datetime,
                              end_date=datetime.combine(datetime.strptime(MediumService.args.end, date_format).date(),
                                                        default_time))
        else:
            scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval, start_date=start)

        # Start the scheduler
        scheduler.start()

    @staticmethod
    def task():
        to_date = datetime.now()
        from_date = to_date - timedelta(days=1)
        to_date = to_date.strftime("%d-%b-%Y")
        from_date = from_date.strftime("%d-%b-%Y")

        search_query = f'(SINCE "{from_date}" BEFORE "{to_date}") FROM "{MediumService.sender}"'
        imap_server = MediumService.open_connection()
        _, message_ids = imap_server.search(None, search_query)
        titles = []
        links = []
        for message_id in message_ids[0].split():
            _, email_data = imap_server.fetch(message_id, '(RFC822)')
            # Parse the email_data using the email module
            raw_email = email_data[0][1]
            body = ''
            email_message = email.message_from_bytes(raw_email)
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
            # Process the extracted information as needed
            # Iterate over the parts of the email
            soup = BeautifulSoup(body, 'html.parser')
            article_divs = soup.find_all('div', attrs={'style': 'display: inline-block; margin-left: 0px;'})
            for article_div in article_divs:
                title_div = article_div.find('div', attrs={'style': 'margin-bottom: 8px;'})
                title = title_div.find('b').text
                # subtitle = article_div.find('div', attrs={
                #     'style': 'font-weight: 400; color: rgba(41, 41, 41, 1); line-height: 28px; font-size: 20px;'}).text
                link = article_div.find('a')['href']
                titles.append(title)
                links.append(link)
        imap_server.close()
        imap_server.logout()
        print(f"titles: {titles}")
        print(f"links: {links}")
        dingtalk_receive.Receive.send_feedcard_msg(titles, links)

    @staticmethod
    def get_help() -> str:
        return ''

    @staticmethod
    def open_connection():
        config = configparser.ConfigParser()
        config.read('../config.ini')
        print(f"username: {config.get('medium', 'username')}, password: {config.get('medium', 'password')}, "
              f"imap_url: {config.get('medium', 'imap_url')}")
        connection = imaplib.IMAP4_SSL(config.get('medium', 'imap_url'))
        connection.login(config.get('medium', 'username'), config.get('medium', 'password'))
        connection.select('Inbox')
        return connection


# Uncomment this to see what actually comes as data
# print(msgs)
if __name__ == '__main__':
    MediumService.scheduler()
