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
        Returns the help message of the service
        """
        raise NotImplementedError
