from typing import List


class BaseScheduledService:
    """
    This class defines basic functions that a scheduled service should implement.
    All Scheduled Service classes are expected to inherit this class.
    """

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
    def scheduler():
        """
        create a scheduler for the task.
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service. This function should be called in process_query.
        """
        raise NotImplementedError
