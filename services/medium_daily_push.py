import datetime
import email
import imaplib
import configparser
import re
from datetime import datetime, timedelta, time
from typing import List, Optional, Callable
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from services.base_shceduled_service import BaseScheduledService


class MediumService(BaseScheduledService):
    scheduler = None
    sender = 'noreply@medium.com'
    send_msg = Optional[Callable[[List[str], List[str]], None]]
    username = None
    password = None
    imap_url = None

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        return ''

    @staticmethod
    def init_service(func_send_feedcard, configs):
        MediumService.send_msg = func_send_feedcard
        print(configs)
        MediumService.username = configs.get('medium', 'username')
        MediumService.password = configs.get('medium', 'password')
        MediumService.imap_url = configs.get('medium', 'imap_url')

    @staticmethod
    def start_scheduler(repeat: bool, start_time: str, end_time=None, cycle=None):
        # Create a scheduler
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(start_time, date_format).date()
        start = datetime.now().date() if start_date < datetime.now().date() else start_date
        default_time = time(8, 0, 0)
        combined_datetime = datetime.combine(start, default_time)
        if MediumService.scheduler is None:
            MediumService.scheduler = BlockingScheduler()

        cycle_interval = cycle * 24 * 60 * 60  # Cycle interval in seconds

        # Schedule the task to run repeatedly
        if end_time is not None:
            MediumService.scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval,
                                            start_date=combined_datetime,
                                            end_date=datetime.combine(datetime.strptime(end_time, date_format).date(),
                                                                      default_time))
        else:
            MediumService.scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval, start_date=start)

        # Start the scheduler if it is not already running
        if not MediumService.scheduler.running:
            MediumService.scheduler.start()

    @staticmethod
    def task():
        to_date = datetime.now()
        from_date = to_date - timedelta(days=1)
        to_date = to_date.strftime("%d-%b-%Y")
        from_date = from_date.strftime("%d-%b-%Y")

        search_query = f'(SINCE "{from_date}" BEFORE "{to_date}") FROM "{MediumService.sender}"'
        imap_server = MediumService.open_connection()
        _, message_ids = imap_server.search(None, search_query)
        image_urls = []
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
            article_divs = soup.find_all('div',
                                         attrs={'style': 'overflow: hidden; margin-bottom: 20px; margin-top: 20px;'})
            for i, article_div in enumerate(article_divs):
                image_div = article_div.select(
                    '[style^="width: 100%; float: left; height: 214px; margin-bottom: 16px;"]')
                if not len(image_div) == 0:
                    match = re.search(r'url\((.*?)\)', image_div[0]['style'])
                    if match:
                        image_urls.append(match.group(1))
                    else:
                        image_urls.append('')
                else:
                    image_urls.append('')
                title_div = article_div.find('div', attrs={'style': 'display: inline-block; margin-left: 0px;'})
                title_div = title_div.find('div', attrs={'style': 'margin-bottom: 8px;'})
                title = title_div.find('b').text
                link = article_div.find('a')['href']
                titles.append(title)
                links.append(link)
        imap_server.close()
        imap_server.logout()
        MediumService.send_msg(titles, links, image_urls)

    @staticmethod
    def get_help() -> str:
        return ''

    @staticmethod
    def open_connection():
        connection = imaplib.IMAP4_SSL(MediumService.imap_url)
        connection.login(MediumService.username, MediumService.password)
        connection.select('Inbox')
        return connection


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../config.ini')
    MediumService.init_service(MediumService.get_help, config)
    MediumService.task()
