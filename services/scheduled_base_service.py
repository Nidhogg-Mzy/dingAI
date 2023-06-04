from typing import List, Callable
from apscheduler.schedulers.background import BackgroundScheduler

class BaseScheduledService:
    """
    This class defines basic functions that a scheduled service should implement.
    All Scheduled Service classes are expected to inherit this class.
    """

    @staticmethod
    def init_service(func_send: Callable, configs: dict) -> None:
        """
        Initialize the service.

        :param func_send: a function that sends message to user
        :param configs: a dict that contains all the configs
        :return: None
        :raises ValueError: if the configs is invalid, which indicates a program bug.
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
    def create_scheduler() -> BackgroundScheduler:
        """
        Create a scheduler for the task that is ready to be started.
        If the scheduler is already created, return the existing scheduler.

        :return: a BackgroundScheduler object, the initialized scheduler
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service. This function should be called in process_query.
        """
        raise NotImplementedError
