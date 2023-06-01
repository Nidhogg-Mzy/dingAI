import configparser
import json
import os
import re
import requests
from typing import List, Iterable

from .base_service import BaseService


class GPTService(BaseService):
    """
    This class is the service that generates text using GPT API provided by OpenAI.
    To use this service, you need to have an API key from OpenAI and provided in
    config['openai']['api_key'].
    """

    _initialized = False

    _ENABLED = None
    _API_KEY = None
    _CACHE_FOLDER = None
    _CHAT_ENABLED = None
    _CHAT_ENDPOINT = None
    _CHAT_MODEL = None
    _MAX_TOKEN = None
    _IMAGE_ENABLED = None

    @staticmethod
    def load_config(configs: dict) -> None:
        # only execute once
        if GPTService._initialized:
            return None
        GPTService._initialized = True

        openai_configs = configs['openai']
        root_dir = configs['project']['root_path']
        # general
        GPTService._ENABLED = openai_configs.getboolean('enabled')
        GPTService._API_KEY = openai_configs['api_key']
        GPTService._CACHE_FOLDER = f"{root_dir}/services/{openai_configs['cache_folder']}"
        os.makedirs(GPTService._CACHE_FOLDER, exist_ok=True)

        # chat function
        GPTService._CHAT_ENABLED = openai_configs.getboolean('chat_enabled')
        GPTService._CHAT_ENDPOINT = openai_configs['chat_endpoint']
        GPTService._CHAT_MODEL = openai_configs['chat_model']
        try:
            GPTService._MAX_TOKEN = int(openai_configs['max_tokens'])
        except ValueError:
            raise ValueError('Invalid max_tokens in config.ini, must be an integer')

        # image function
        GPTService._IMAGE_ENABLED = openai_configs.getboolean('image_enabled')

    # pylint: disable=too-many-branches
    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        """
        Process GPT service query.

        :param query: a list of strings, the first string must be either 'chat' or 'image',
            the rest of the strings are the prompt for the query.
        :param user_id: a string, the user id of the user who sent the query.
        :return: a string, the response of the query, in Markdown syntax.
        :raises ValueError: if the query is invalid.
        """
        # must be init before query
        if not GPTService._initialized:
            return '[Error] not initialized before query, please contact the administrator.'
        # validate query
        if len(query) == 0:
            raise ValueError('Invalid query: query length is 0, but is passed into GPTService')
        if query[0] not in ['chat', 'chathistory', 'chathist', 'chatload', 'chatsave', 'chatdiscard', 'chatdelete',
                            'image']:
            raise ValueError(f'Invalid query: query[0] = "{query[0]}", but is passed into GPTService')
        # help query
        if len(query) > 1 and query[1] == 'help':
            return GPTService.get_help()

        # check if the service is enabled
        if not GPTService._ENABLED:
            return '[Error] OpenAI services are not enabled. Please contact the administrator.'
        # check if the function is enabled
        if query[0] == 'chat' and not GPTService._CHAT_ENABLED:
            return '[Error] Chat function is not enabled. Please contact the administrator.'
        if query[0] == 'image' and not GPTService._IMAGE_ENABLED:
            return '[Error] Image function is not enabled. Please contact the administrator.'

        # chat function #
        if query[0] == 'chat':
            # if user only pass in func name, but no prompt, return help message
            if len(query) == 1:
                return f'[Error] Your query is not complete.\n\n{GPTService.get_help()}'
            # always write to temp file, then depending on whether user save or discard it,
            # either rename to a meaningful name provided by user, or delete it
            os.makedirs(f'{GPTService._CACHE_FOLDER}/{user_id}', exist_ok=True)
            cache_file = f'{GPTService._CACHE_FOLDER}/{user_id}/temp.json'
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    chat_history = json.load(f)
            except FileNotFoundError:
                chat_history = []

            # add the user's message to the chat history
            prompt = ' '.join(query[1:])
            chat_history.append({"role": "user", "content": prompt})

            # call API to generate a response
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GPTService._API_KEY}"
            }
            data = {
                "model": GPTService._CHAT_MODEL,
                "messages": chat_history,
                "max_tokens": GPTService._MAX_TOKEN
            }
            response = requests.post(GPTService._CHAT_ENDPOINT, headers=headers, json=data)
            response = json.loads(response.content.decode("utf-8"))

            # add the response to the chat history
            chat_history.append(response['choices'][0]['message'])
            # save the chat history to the cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f)
            # return the response
            return response['choices'][0]['message']['content']
        elif query[0] in ['chathistory', 'chathist']:
            # list histories we have
            user_folder = f'{GPTService._CACHE_FOLDER}/{user_id}'
            os.makedirs(user_folder, exist_ok=True)  # in case user didn't have a folder
            all_files = os.listdir(user_folder)
            # use regex to filter all files in format (%d+)-(.*).json
            pattern = re.compile(r"(\d+)-(.*)\.json")
            history_files: List[str] = list(filter(pattern.match, all_files))

            # if no history, return no hist msg
            if len(history_files) == 0:
                return "You don't have any chat history yet. "

            hist_list = "Your chat histories:\n"
            for history_file in history_files:
                num, name = pattern.match(history_file).group(1), pattern.match(history_file).group(2)
                # Markdown ordered list style
                hist_list += f'{num}. {name}\n'

            hist_list += "\nTo load a history, use *chatload <history number>*"
            return hist_list

        elif query[0] == 'chatload':
            # load specific chat to temp.json
            # don't touch original chat history unless user save it
            if len(query) < 2:
                return '[Error] You need to specify history number to load a chat history'

            history_no = query[1]
            try:
                history_no = int(history_no)
            except ValueError:
                return '[Error] History no needs to be an integer number. If you think this is an error, ' \
                       'please contact administrator. '

            user_folder = f'{GPTService._CACHE_FOLDER}/{user_id}'
            os.makedirs(user_folder, exist_ok=True)  # in case user didn't have a folder
            all_files = os.listdir(user_folder)
            # use regex to find history in format ${history_no}-(.*).json
            pattern = re.compile(rf"{history_no}-(.*)\.json")
            history_files: List[str] = list(filter(pattern.match, all_files))
            if len(history_files) == 0:
                return '[Error] History no is not valid. If you think this is an error, please contact administrator.'
            if len(history_files) > 1:
                return '[Error] Multiple history files found. This is likely to be a software bug, please contact ' \
                       'administrator. '

            # history file found! load into temp.json
            history_file = history_files[0]
            with open(f'{user_folder}/{history_file}', 'r', encoding='utf-8') as f:
                history_content = f.read()
            with open(f'{user_folder}/temp.json', 'w+', encoding='utf-8') as f:
                f.write(history_content)
            # prompt success, and display last query and answer
            last_query = json.loads(history_content)[-1]['content']
            to_return = f'History {history_no} loaded successfully. The last message was: \n\n ' \
                        f'**>** {last_query}\n'

            return to_return

        elif query[0] == 'chatdelete':
            if len(query) < 2:
                return '[Error] You need to specify history number to delete a chat history'

            history_no = query[1]
            try:
                history_no = int(history_no)
            except ValueError:
                return '[Error] History no needs to be an integer number. If you think this is an error, ' \
                       'please contact administrator. '

            user_folder = f'{GPTService._CACHE_FOLDER}/{user_id}'
            os.makedirs(user_folder, exist_ok=True)  # in case user didn't have a folder
            all_files = os.listdir(user_folder)
            file_to_delete: list[str] = list(filter(lambda x: x.startswith(f'{history_no}-'), all_files))
            if len(file_to_delete) == 0:
                return f'[Error] Cannot find history with no {history_no}. If you think this is an error, please ' \
                       f'contact administrator. '
            if len(file_to_delete) > 1:
                return '[Error] Multiple history files found. This is likely to be a software bug, please contact ' \
                       'administrator. '

            # delete the file
            os.remove(f'{user_folder}/{file_to_delete[0]}')

            # for remaining histories, rename them with new history no
            for file in all_files:
                # use regex to extract history no
                pattern = re.compile(r"(\d+)-(.*)\.json")
                if pattern.match(file) is None:
                    continue
                old_history_no = pattern.match(file).group(1)
                if int(old_history_no) > history_no:
                    new_history_no = int(old_history_no) - 1
                    os.rename(f'{user_folder}/{file}',
                              f'{user_folder}/{new_history_no}-{pattern.match(file).group(2)}.json')

            return f'Successfully deleted history {history_no}.'

        elif query[0] == 'chatsave':
            if len(query) < 2:
                return '[Error] You need to specify a name to save this chat history'

            # we need to find out the last history no
            user_folder = f'{GPTService._CACHE_FOLDER}/{user_id}'
            os.makedirs(user_folder, exist_ok=True)  # in case user didn't have a folder
            all_files = os.listdir(user_folder)
            pattern = re.compile(r"(\d+)-(.*)\.json")
            history_files: Iterable[str] = filter(pattern.match, all_files)

            next_no = 1     # the next available history no

            for history_file in history_files:
                num = pattern.match(history_file).group(1)
                next_no = max(next_no, int(num) + 1)

            # save the current chat history
            with open(f'{user_folder}/{next_no}-{query[1]}.json', 'w+', encoding='utf-8') as f:
                with open(f'{user_folder}/temp.json', 'r', encoding='utf-8') as temp:
                    f.write(temp.read())

            return f'Successfully saved current chat history as **{next_no}. {query[1]}**.' \
                   'You can view all your chat histories using *chathistory*.'

        elif query[0] == 'chatdiscard':
            cache_file = f'{GPTService._CACHE_FOLDER}/{user_id}/temp.json'
            if os.path.exists(cache_file):
                os.remove(cache_file)

            return 'Successfully **discarded** current chat session. \n However, if you loaded a chat history, ' \
                   'it will still be there. You can delete it using *chatdelete <history no>*.'

        # image function #
        # TODO: implement image function
        raise NotImplementedError('Image function is not implemented yet')

    @staticmethod
    def get_help() -> str:
        return '**GPTService is a service that uses ChatGPT-3.5 API provided by OpenAI to generate text.** \n\n ' \
               '**[Basic Usage]** \n ' \
               '- *chat <message>*: send <message> to GPT, and get the response.\n' \
               '**[Manipulate history]** \n ' \
               '- *chathistory* or *chathist*: list the history chats with GPT.\n' \
               '- *chatload <history no>*: continue the corresponding history chat, <history no> can be ' \
               'obtained by *chathistory*. **Notice that current chat session will be discarded.**\n' \
               '- *chatdelete <history no>*: delete the given chat history. \n\n ' \
               '**[Manipulate current session]** \n ' \
               '- *chatsave <name>*: Quit current GPT session, and **save** chats history with given name.\n' \
               '- *chatdiscard*: (Encouraged) Quit current GPT session, and **discard** current chat content. ' \
               'However, if you want to delete a chat history, you need to use *chatdelete <history no>*. \n '


if __name__ == '__main__':
    config_parser = configparser.ConfigParser()
    config_parser.read('./config.ini')
    GPTService.load_config(config_parser)
    print(GPTService.process_query(['chat'], 'test'))
    print(GPTService.process_query(['chat', 'help'], 'test'))
    print(GPTService.process_query(['chat', 'who', 'am', 'i'], 'test'))
