import datetime
import email
import imaplib
import re
import configparser
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from services.scheduled_base_service import BaseScheduledService


class MediumService(BaseScheduledService):
    """
    This class is the service that push medium daily digest.
    """
    scheduler = None
    sender = None
    send_msg: Callable[[List[str], List[str], List[str]], None] = lambda *args: None
    username: Optional[str] = None
    password: Optional[str] = None
    imap_url: Optional[str] = None
    repeat: Optional[bool] = None
    start_time: Optional[str] = None
    cycle: Optional[int] = None
    end_time: Optional[str] = None

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        """
        this method is leave for further use to modify the service start_time, end_time and cycle via dingtalk
        """
        return ''

    @staticmethod
    def init_service(func_send, configs):
        MediumService.send_msg = func_send
        MediumService.sender = configs.get('medium', 'sender')
        MediumService.username = configs.get('medium', 'username')
        MediumService.password = configs.get('medium', 'password')
        MediumService.imap_url = configs.get('medium', 'imap_url')
        MediumService.start_time = configs.get('medium', 'start_time')
        try:
            MediumService.repeat = bool(configs.get('medium', 'repeat'))
        except ValueError as e:
            raise ValueError(f'repeat should be boolean, now is {configs.get("medium", "repeat")}') from e
        try:
            MediumService.cycle = int(configs.get('medium', 'cycle'))
        except ValueError as e:
            raise ValueError(f'cycle should be int, now is {configs.get("medium", "cycle")}') from e
        MediumService.end_time = configs.get('medium', 'end_time')

    @staticmethod
    def create_scheduler():
        # return if the scheduler is already created
        if MediumService.scheduler is not None:
            return MediumService.scheduler
        # Create a scheduler
        MediumService.scheduler = BackgroundScheduler()
        date_format = "%Y-%m-%d-%H:%M"
        start_date = datetime.strptime(MediumService.start_time, date_format)
        start = datetime.now() if start_date < datetime.now() else start_date
        end = datetime.strptime(MediumService.end_time, date_format)

        cycle_interval = MediumService.cycle * 24 * 60 * 60  # Cycle interval in seconds

        MediumService.scheduler.add_job(MediumService.task, 'interval', seconds=cycle_interval,
                                        start_date=start,
                                        end_date=end)
        return MediumService.scheduler

    @staticmethod
    def task():
        """
        this method is the task of getting today's medium email and extract the data we want
        """
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
            try:
                raw_email = email_data[0][1]
            except IndexError as e:
                # clean up the connection on error
                imap_server.close()
                imap_server.logout()
                raise IndexError('IndexError: email_data[0][1] index out of range') from e
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
            for article_div in article_divs:
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
        """
        this method is leave for further use to get help from service when user try to use process query
        from dingtalk
        """
        return ''

    @staticmethod
    def open_connection():
        """
        this method is used to open connection to gmail imap server
        """
        connection = imaplib.IMAP4_SSL(MediumService.imap_url)
        connection.login(MediumService.username, MediumService.password)
        connection.select('Inbox')
        return connection


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../config.ini')
    MediumService.init_service(MediumService.get_help, config)
    MediumService.task()
