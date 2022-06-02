from database import DataBase


class UserOperation:
    user_list = {}  # format: {qq_account: leetcode_username}

    @staticmethod
    @DataBase.retry_if_disconnected
    def update_user_list() -> None:
        """
        This function read latest user list from database and store in UserOperation.user_list
        """
        UserOperation.user_list = DataBase.get_user()

    @staticmethod
    @DataBase.retry_if_disconnected
    def register(qq: str, leetcode: str) -> tuple:
        """
        Given qq account and leetcode username, register a new user. This function won't raise any exception.
        :param qq: qq account
        :param leetcode: leetcode username
        :return: A tuple, first item is a boolean, indicating the operation is successful or not.
                 Second item is a string, if successful, it indicates the result message, e.g., "Successfully registered.",
                 otherwise, it stores the error message
        """
        if qq in UserOperation.user_list:
            old_leetcode = UserOperation.user_list[qq]
            DataBase.update_user(qq, leetcode)
            UserOperation.update_user_list()
            
            # check if the update is really successful TODO: do we really need this?
            new_leetcode = UserOperation.user_list[qq]
            if new_leetcode == leetcode:
                return True, f"Successfully update your leetcode username from {old_leetcode} to {leetcode}."
            return False, "Ahh, something wrong during register, please try again"
        else:
            DataBase.insert_user(qq, leetcode)
            UserOperation.update_user_list()
        
            new_leetcode = UserOperation.user_list[qq]
            if new_leetcode == leetcode:
                return True, f"Successfully set your leetcode username to {leetcode}."
            return False, "Ahh, something wrong during register, please try again"

    @staticmethod
    def get_leetcode(qq: str) -> tuple:
        """
        Given qq account, return the user's leetcode username.

        :param qq: qq account
        :return: A tuple, first item is a boolean, indicating the operation is successful or not,
        currently the operation will fail only if the user has not registered.
        If first item is True, then second item is a string, representing the user's leetcode username
        """
        if qq not in UserOperation.user_list:
            return False, "Error: User not registered."
        return True, UserOperation.user_list[qq]

    @staticmethod
    @DataBase.retry_if_disconnected
    def delete_user(qq: str) -> bool:
        """
        [WARNING] This function should only be called from testing.
        Delete a user record from the user database given qq account.
        :param qq: given qq account to delete
        :return: True, if the user is successfully deleted; False,
        if user not in database or database file cannot found.
        """
        if qq not in UserOperation.user_list:
            return False
        
        DataBase.delete_user(qq)
        del UserOperation.user_list[qq]
        return True


if __name__ == "__main__":
    # Simple Test

    UserOperation.update_user_list()
    print(UserOperation.user_list)

    print(UserOperation.register("12345678", "test1"))
    print(UserOperation.user_list)
    print(UserOperation.get_leetcode("12345678"))

    print(UserOperation.register("12345678", "test2"))
    print(UserOperation.user_list)
    print(UserOperation.get_leetcode("12345678"))

    print(UserOperation.delete_user("12345678"))
    print(UserOperation.user_list)
