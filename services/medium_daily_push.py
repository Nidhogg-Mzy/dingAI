import datetime
import email
import imaplib
import re
import configparser
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from services.scheduled_base_service import BaseScheduledService


class MediumService(BaseScheduledService):
    scheduler = None
    sender = None
    send_msg: Optional[Callable[[List[str], List[str], List[str]], None]] = None
    username: Optional[str] = None
    password: Optional[str] = None
    imap_url: Optional[str] = None
    repeat = None
    start_time = None
    cycle: Optional[str] = None
    end_time: Optional[str] = None

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        return ''

    @staticmethod
    def init_service(func_send_feedCard, configs):
        MediumService.send_msg = func_send_feedCard
        MediumService.sender = configs.get('medium', 'sender')
        MediumService.username = configs.get('medium', 'username')
        MediumService.password = configs.get('medium', 'password')
        MediumService.imap_url = configs.get('medium', 'imap_url')
        MediumService.start_time = configs.get('medium', 'start_time')
        try:
            MediumService.repeat = bool(configs.get('medium', 'repeat'))
        except ValueError:
            raise ValueError('repeat should be boolean, now is {}'.format(configs.get('medium', 'repeat')))
        try:
            MediumService.cycle = int(configs.get('medium', 'cycle'))
        except ValueError:
            raise ValueError('cycle should be int, now is {}'.format(configs.get('medium', 'cycle')))
        MediumService.end_time = configs.get('medium', 'end_time')

    @staticmethod
    def start_scheduler():
        # Create a scheduler
        date_format = "%Y-%m-%d-%H:%M"
        start_date = datetime.strptime(MediumService.start_time, date_format)
        start = datetime.now() if start_date < datetime.now() else start_date
        end = datetime.strptime(MediumService.end_time, date_format)
        if MediumService.scheduler is None:
            MediumService.scheduler = BlockingScheduler()

        cycle_interval = MediumService.cycle * 24 * 60 * 60  # Cycle interval in seconds

        MediumService.scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval,
                                        start_date=start,
                                        end_date=end)

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
            # To iterate over the parts of the email
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
