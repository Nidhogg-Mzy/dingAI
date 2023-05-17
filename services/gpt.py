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

    _initialized = False

    _ENABLED = None
    _API_KEY = None
    _CACHE_FOLDER = None
    _CHAT_ENABLED = None
    _CHAT_MODEL = None
    _IMAGE_ENABLED = None

    @staticmethod
    def load_config(configs: dict) -> None:
        # only execute once
        if GPTService._initialized:
            return None

        openai_configs = configs['openai']
        # general
        GPTService._ENABLED = openai_configs.getboolean('enabled')
        GPTService._API_KEY = openai_configs['api_key']
        GPTService._CACHE_FOLDER = openai_configs['cache_folder']
        os.makedirs(GPTService._CACHE_FOLDER, exist_ok=True)

        # chat function
        GPTService._CHAT_ENABLED = openai_configs.getboolean('chat_enabled')
        GPTService._CHAT_MODEL = openai_configs['chat_model']

        # image function
        GPTService._IMAGE_ENABLED = openai_configs.getboolean('image_enabled')

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
            raise ValueError('[Error] not initialized before query, please contact the administrator.')
        # validate query
        if len(query) == 0:
            raise ValueError(f'Invalid query: query length is 0, but is passed into GPTService')
        if query[0] not in ['chat', 'image']:
            raise ValueError(f'Invalid query: query[0] = "{query[0]}", but is passed into GPTService')
        # if user only pass in func name, but no prompt, return help message
        if len(query) == 1:
            return f'[Error] Your query is not complete.\n\n{GPTService.get_help()}'
        if query[1] == 'help':
            return GPTService.get_help()

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
            cache_file = f'{GPTService._CACHE_FOLDER}/{user_id}.json'
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
                max_tokens=500      # max length of generated completion
            )
            # add the response to the chat history
            chat_history.append(response.choices[0].message)
            # save the chat history to the cache file
            with open(cache_file, 'w') as f:
                json.dump(chat_history, f)
            # return the response
            return response.choices[0].message.content

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
    print(GPTService.process_query(['chat'], 'test'))
    print(GPTService.process_query(['chat', 'help'], 'test'))
    print(GPTService.process_query(['chat', 'who', 'am', 'i'], 'test'))
