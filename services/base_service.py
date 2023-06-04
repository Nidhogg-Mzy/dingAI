from typing import List

class BaseService:
    """
    This class defines basic functions that a service should implement.
    All Service classes are expected to inherit this class.
    """

    @staticmethod
    def load_config(configs: dict) -> None:
        """
        Load the given config to this service. This method should be called before processing
        any query, and should guarantee to be executed only once, no matter how many times it's called.

        :param configs: a dict, the complete configs loaded from config.ini

        :raises ValueError: if the config is invalid, which indicates a program bug.
        """
        raise NotImplementedError

    @staticmethod
    def process_query(query: List[str], user_id: str) -> str:
        """
        Processes the query that user passed in, and return a reply.

        :param query: a list of strings that is the query from front-end, an example can be ['ddl', 'today']
        :param user_id: the account of the user who perform the query.
        :return: a string that is the result of the query to be displayed to user
        :raises ValueError: if the query or user_id is invalid, which indicates a program bug.
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service. This function should be called in process_query.
        """
        raise NotImplementedError
