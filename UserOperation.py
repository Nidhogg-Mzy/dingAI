from os import path
import json

class UserOperation:
    def __init__(self):
        self.user_list = {}     # format: {qq_account: leetcode_username}
        self.data_file = "user.json"
        # read user_list from data file
        if not path.isfile(self.data_file):
            raise FileNotFoundError("User data file not found, check if user.json exists.")

        with open(self.data_file, 'r') as f:
            raw_user_list = json.load(f)    # this reads a list of dict

        for qq in raw_user_list:
            self.user_list[qq] = raw_user_list[qq]

    def update_data(self):
        # Check if data file exists
        if not path.isfile(self.data_file):
            raise FileNotFoundError("User data file not found, check if user.json exists.")
        # write stored data to file
        with open(self.data_file, 'w') as json_file:
            json.dump(self.user_list, json_file, indent=4, separators=(',', ': '))

    def register(self, qq: str, leetcode: str) -> tuple[bool, str]:
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
            self.user_list[qq] = leetcode
            try:
                self.update_data()
            except FileNotFoundError:
                return False, "Failed to register. User data file not found, check if user.json exists."
            else:
                return True, f"Successfully update your leetcode username from {old_leetcode} to {leetcode}."
        else:
            self.user_list[qq] = leetcode
            try:
                self.update_data()
            except FileNotFoundError:
                return False, "Failed to register. User data file not found, check if user.json exists."
            else:
                return True, f"Successfully set your leetcode username to {leetcode}."

    def get_leetcode(self, qq: str) -> str:
        """
        Given qq account, return the user's leetcode username.
        Raise exception if the user is not registered.
        :param qq: qq account
        :return: leetcode username
        """
        if qq not in self.user_list.keys():
            raise KeyError(f"User {qq} is not registered.")
        else:
            return self.user_list[qq]


if __name__ == "__main__":
    # Simple Test
    user_operation = UserOperation()

    res, msg = user_operation.register("123456789", "testing")
    print(f"result: {res}, message: {msg}")

    # this function may raise KeyError when user not exist
    try:
        leetcode_username = user_operation.get_leetcode("12")
    except KeyError:
        print("User is not registered.")
    else:
        print(f"username: {leetcode_username}")

    try:
        leetcode_username = user_operation.get_leetcode("123456789")
    except KeyError:
        print("User is not registered.")
    else:
        print(f"username: {leetcode_username}")
