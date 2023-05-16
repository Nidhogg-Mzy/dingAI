import configparser
import json
import os
from typing import List, Optional

import openai

from base_service import BaseService


class GPTService(BaseService):
    """
    This class is the service that generates text using GPT-3 API provided by OpenAI.
    To use this service, you need to have an API key from OpenAI and provided in
    config['openai']['api_key'].
    """
    _config = configparser.ConfigParser()
    _config.read('../config.ini')
    _OPENAI_CONFIGS = _config['openai']
    # general
    _ENABLED = _OPENAI_CONFIGS.getboolean('enabled')
    _API_KEY = _OPENAI_CONFIGS['api_key']
    _CACHE_FOLDER = _OPENAI_CONFIGS['cache_folder']
    os.makedirs(_CACHE_FOLDER, exist_ok=True)

    # chat function
    _CHAT_ENABLED = _OPENAI_CONFIGS.getboolean('chat_enabled')
    _CHAT_MODEL = _OPENAI_CONFIGS['chat_model']

    # image function
    _IMAGE_ENABLED = _OPENAI_CONFIGS.getboolean('image_enabled')

    @staticmethod
    def process_query(query: List[str], extra_info: Optional[dict] = None) -> str:
        """
        Process GPT service query.

        :param query: a list of strings, the first string must be either 'chat' or 'image',
            the rest of the strings are the prompt for the query.
        :param extra_info: a dictionary that contains extra information. Possible fields:
            'user_id' (mandatory): a string, the user id of the user who sent the query.
            'use_cache' (optional): a boolean, whether to use cache. Default is True. Note that
                if this is set to False, the cache will be deleted permanently.
        :return: a string, the response of the query.
        :raises ValueError: if the query is invalid.
        """
        # validate query
        if len(query) == 0:
            raise ValueError(f'Invalid query: query length is 0, but is passed into GPTService')
        if query[0] not in ['chat', 'image']:
            raise ValueError(f'Invalid query: query[0] = "{query[0]}", but is passed into GPTService')
        if extra_info is None or 'user_id' not in extra_info:
            raise ValueError(f'To use GPTService, "user_id" must be provided in extra_info')
        # if user only pass in func name, but no prompt, return help message
        if len(query) == 1 or query[1] == 'help':
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
            prompt = ' '.join(query[1:])
            chat_history.append({"role": "user", "content": prompt})
            print(chat_history)
            # call OpenAI API to generate a response
            response = openai.ChatCompletion.create(
                model=GPTService._CHAT_MODEL,
                messages=chat_history,
            )
            # add the response to the chat history
            chat_history.append(response.choices[0].message)
            # save the chat history to the cache file
            with open(cache_file, 'w') as f:
                json.dump(chat_history, f)
            # return the response
            return response.choices[0].message

        # image function #
        raise NotImplementedError(f'Image function is not implemented yet')

    @staticmethod
    def get_help() -> str:
        return f'**GPTService is a service that uses ChatGPT-3.5 API provided by OpenAI to generate text.**\n' \
               f'[Usage]\n' \
               f'- chat <message>\n' \
               f'- image <message> (not available)\n' \
               f'[Example]\n' \
               f'- chat who are you\n'


if __name__ == '__main__':
    print(GPTService.process_query(['chat'], {'user_id': 'test'}))
    print(GPTService.process_query(['chat', 'help'], {'user_id': 'test'}))
    print(GPTService.process_query(['chat', 'who', 'am', 'i'], {'user_id': 'test'}))
