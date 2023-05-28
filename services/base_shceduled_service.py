class BaseScheduledService:
    """
    This class defines basic functions that a scheduled service should implement.
    All Scheduled Service classes are expected to inherit this class.
    """

    @staticmethod
    def scheduler(repeat: bool, cycle=None, start=None, end=None):
        """
        create a scheduler for the task.

        :param repeat: if the task is executed repeatedly
        :param cycle: the repeat cycle of a task. Required only if is a repeat task.
        :param start: the time to start the task.
        :param end: the time to end a task.
        :return: a string that is the result of the query to be displayed to user
        :raises ValueError: if the query or extra_info is invalid
        """
        if repeat and (cycle is None or start is None or end is None):
            return 'Please give the period of the cycle, the start and end date.'
        if not repeat and start != end:
            return 'give a specific time point please'

    @staticmethod
    def get_help() -> str:
        """
        Returns the help message of the service. This function should be called in process_query.
        """
        raise NotImplementedError
