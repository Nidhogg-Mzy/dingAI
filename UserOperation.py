from database import DataBase


class UserOperation:
    def __init__(self):
        self.user_list = {}  # format: {qq_account: leetcode_username}

    def update_user_list(self) -> bool:
        result = DataBase.get_user()
        if not result[0]:
            return False
        self.user_list = result[1]
        return True

    def register(self, qq: str, leetcode: str) -> tuple:
        """
        Given qq account and leetcode username, register a new user. This function won't raise any exception.
        :param qq: qq account
        :param leetcode: leetcode username
        :return: A tuple, first item is a boolean, indicating the operation is successful or not.
                 Second item is a string, if successful, it indicates the result message, e.g., "Successfully registered.",
                 otherwise, it stores the error message
        """
        if qq in self.user_list:
            old_leetcode = self.user_list[qq]
            upd_res = DataBase.update_user(qq, leetcode)
            upd_local_res = self.update_user_list()
            if upd_res and upd_local_res:
                return True, f"Successfully update your leetcode username from {old_leetcode} to {leetcode}."
            return False, "Failed to connect to database."
        else:
            if DataBase.insert_user(qq, leetcode) and self.update_user_list():
                return True, f"Successfully set your leetcode username to {leetcode}."
            return False, "Failed to connect to database."

    def get_leetcode(self, qq: str) -> tuple:
        """
        Given qq account, return the user's leetcode username.

        :param qq: qq account
        :return: A tuple, first item is a boolean, indicating the operation is successful or not,
        currently the operation will fail only if the user has not registered.
        If first item is True, then second item is a string, representing the user's leetcode username
        """
        if qq not in self.user_list:
            return False, "Error: User not registered."
        return True, self.user_list[qq]

    def delete_user(self, qq: str) -> bool:
        """
        [WARNING] This function should only be called from testing.
        Delete a user record from the user database given qq account.
        :param qq: given qq account to delete
        :return: True, if the user is successfully deleted; False,
        if user not in database or database file cannot found.
        """
        if qq not in self.user_list:
            return False
        if DataBase.delete_user(qq):
            del self.user_list[qq]
            return True
        return False


if __name__ == "__main__":
    # Simple Test
    user_operation = UserOperation()

    res, msg = user_operation.register("123456789", "testing")
    print(f"result: {res}, message: {msg}")

    # this function returns false when user does not exist
    status, username = user_operation.get_leetcode("12")
    if not status:
        print("User is not registered.")
    else:
        print(f"username: {username}")

    status, username = user_operation.get_leetcode("123456789")
    if not status:
        print("User is not registered.")
    else:
        print(f"username: {username}")

    status, msg = user_operation.register("2220038250", "enor2017")
    print(f"result: {status}, message: {msg}")
    status, username = user_operation.get_leetcode("2220038250")
    if not status:
        print("User is not registered.")
    else:
        print(f"username: {username}")
