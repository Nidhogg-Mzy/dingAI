from base_service import BaseService

from typing import List, Optional
import configparser
import json

import openai

class GPTService(BaseService):
    """
    This class is the service that generates text using GPT-3 API provided by OpenAI.
    To use this service, you need to have an API key from OpenAI and provided in
    config['openai']['api_key'].
    """
    _config = configparser.ConfigParser()
    _config.read('config.ini')
    _OPENAI_CONFIGS = _config['openai']
    # general
    _ENABLED = _OPENAI_CONFIGS.getboolean('enabled')
    _API_KEY = _OPENAI_CONFIGS['api_key']
    _CACHE_FOLDER = _OPENAI_CONFIGS['cache_folder']

    # chat function
    _CHAT_ENABLED = _OPENAI_CONFIGS.getboolean('chat_enabled')
    _CHAT_MODEL = _OPENAI_CONFIGS['chat_model']

    # image function
    _IMAGE_ENABLED = _OPENAI_CONFIGS.getboolean('image_enabled')

    @staticmethod
    def process_query(query: List[str], extra_info: Optional[dict] = None) -> str:
        # validate query
        if len(query) == 0:
            raise ValueError(f'Invalid query: query length is 0, but is passed into GPTService')
        if query[0] not in ['chat', 'image']:
            raise ValueError(f'Invalid query: query[0] = "{query[0]}", but is passed into GPTService')
        if extra_info is None or 'user_id' not in extra_info:
            raise ValueError(f'To use GPTService, "user_id" must be provided in extra_info')
        # if user only pass in func name, but no prompt, return help message
        if len(query) == 1:
            return f'[Error] Your query is not complete.\n\n{GPTService.get_help()}'

        # check if the service is enabled
        if not GPTService._ENABLED:
            return '[Error] OpenAI services are not enabled. Please contact the administrator.'
        # check if the function is enabled
        if query[0] == 'chat' and not GPTService._CHAT_ENABLED:
            return '[Error] Chat function is not enabled. Please contact the administrator.'
        if query[0] == 'image' and not GPTService._IMAGE_ENABLED:
            return '[Error] Image function is not enabled. Please contact the administrator.'

        # initialize OpenAI API
        openai.api_key = GPTService._API_KEY

        # chat function #
        if query[0] == 'chat':
            # check if there is a cache file (json format) for this user,
            # if there is, retrieve the chat history, otherwise, create a new cache file
            cache_file = f'{GPTService._CACHE_FOLDER}/{extra_info["user_id"]}.json'
            try:
                with open(cache_file, 'r') as f:
                    chat_history = json.load(f)
            except FileNotFoundError:
                chat_history = []

            # add the user's message to the chat history
            chat_history.append(query[1])
            # call OpenAI API to generate a response
            response = openai.Completion.create(
                model=GPTService._CHAT_MODEL,
                messages=chat_history,
            )
            # add the response to the chat history
            chat_history.append(response['choices'][0]['message'])
            # save the chat history to the cache file
            with open(cache_file, 'w') as f:
                json.dump(chat_history, f)
            # return the response
            return response['choices'][0]['text']

        ### image function ###



