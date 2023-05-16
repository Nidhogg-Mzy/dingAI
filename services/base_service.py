from typing import List, Optional

class BaseService:
    """
    This class defines basic functions that a service should implement.
    All Service classes are expected to inherit this class.
    """

    @staticmethod
    def process_query(query: List[str], extra_info: Optional[dict] = None) -> str:
        """
        Processes the query that user passed in, and return a reply.

        :param query: a list of strings that is the query from front-end, an example can be ['ddl', 'today']
        :param extra_info: optional, a dict that contains extra information that the service may need,
            for example, the account of the user who perform the query.
        :return: a string that is the result of the query to be displayed to user
        :raises ValueError: if the query or extra_info is invalid
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service. This function should be called in process_query.
        """
        raise NotImplementedError


class APIService(BaseService):
    """
    This class defines what an API service should implement.
    An API service is a service that simply performs an API call and returns the result.
    """

    # The URL of the API, subclass needs to override this
    # force subclasses to override this
    API_URL: str = ''

    @staticmethod
    def make_api_call(payload: str) -> str:
        """
        Makes an API call to the API_URL, and returns the result.
        Subclass may override this method to customize the API call.

        :param payload: a string that is the payload to be sent to the API
        :return: a string that is the result of the API call
        :raises: APIError if the API call fails
        """
        raise NotImplementedError

    @staticmethod
    def process_query(query: List[str], extra_info: Optional[dict] = None) -> str:
        """
        Processes the query that user passed in, and return a reply.
        If subclass does not override this method, it will simply make an API call
        with the query concatenated with spaces as the payload, and return the result.

        :param query: a list of strings that is the query from front-end,
        an example can be ['ddl', 'today']
        :param extra_info: optional, a dict that contains extra information that the service may need,
        for example, the account of the user who perform the query.
        :return: a string that is the result of the query to be displayed to user
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service
        """
        raise NotImplementedError

    class APIError(Exception):
        """
        This class defines an exception that is raised when the API call fails.
        """
        def __init__(self, message: str = 'API call failed'):
            super().__init__(message)
