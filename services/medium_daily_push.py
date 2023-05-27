import email
import imaplib
import configparser

username = 'XXXXXXXXX'
password = 'askdjf'
imap_url = 'imap.gmail.com'


def open_connection():
    # config = configparser.ConfigParser()
    # config.read('../config.ini')
    # print(f"username: {config.get('medium', 'username')}, password: {config.get('medium', 'password')}, imap_url: {config.get('medium', 'imap_url')}")
    # connection = imaplib.IMAP4_SSL(config.get('medium', 'imap_url'))
    # connection.login(config.get('medium', 'username'), config.get('medium', 'password'))
    connection = imaplib.IMAP4_SSL(imap_url)
    connection.login(username, password)
    connection.select('Inbox')
    return connection


# Uncomment this to see what actually comes as data
# print(msgs)

if __name__ == '__main__':
    from_date = '25-May-2023'
    to_date = '26-May-2023'  # Use the next day to include all emails from May 25
    sender = 'noreply@medium.com'
    search_query = f'(SINCE "{from_date}" BEFORE "{to_date}") FROM "{sender}"'
    imap_server = open_connection()
    status, message_ids = imap_server.search(None, search_query)
    for message_id in message_ids[0].split():
        status, email_data = imap_server.fetch(message_id, '(RFC822)')
        # Parse the email_data using the email module
        raw_email = email_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Extract the desired information
        title = email_message['Subject']
        sender = email.utils.parseaddr(email_message['From'])[1]
        body = ''

        if email_message.is_multipart():
            for part in email_message.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8')

        # Process the extracted information as needed
        print("Title:", title)
        print("Sender:", sender)
        print("Body:", body)
    imap_server.close()
    imap_server.logout()
