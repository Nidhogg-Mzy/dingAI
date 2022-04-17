"""
A ddl in json looks like:
[
  {
    "title": "COMP2012 PA2",
    "date": "2022-04-02",
    "participants": ["2220038250", "12345678"],
    "description": "Due at 23:59 PM."
  },
  {
    "title": "COMP2211 Midterm Exam",
    "date": "2022-04-02",
    "participants": ["2220038250", "3429582673"],
    "description": "2PM - 4PM. Join at 1PM for attendance checking."
  }
]
"""
import datetime
import json
import re


class DDLService:
    def __init__(self):
        self.filename = "ddl.json"
        self.ddl_list = []
        self.load_ddl_from_file()

    def load_ddl_from_file(self):
        """
        Load ddl list from file, store the result in self.ddl_list
        """
        with open(self.filename, "r") as f:
            self.ddl_list = json.load(f)  # A list of dict

    def get_ddl(self, predicate: lambda ddl: bool) -> list:
        """
        Return a list of ddl that satisfy the predicate
        :param predicate: a function that takes a ddl and returns True or False based on your predicate
        :return: a list of ddl that satisfy the predicate
        """
        return list(filter(predicate, self.ddl_list))

    def store_ddl(self):
        """
        Store the self.ddl_list to file, we don't handle any exception here.
        """
        with open(self.filename, "w") as f:
            json.dump(self.ddl_list, f, indent=4, separators=(',', ': '))

    def remove_expired_ddl(self):
        """
        Remove all the expired ddl from self.ddl_list. This should be called periodically to
        tidy database.
        """
        self.ddl_list = list(filter(lambda ddl: ddl['date'] >= str(datetime.date.today()), self.ddl_list))
        self.store_ddl()

    @staticmethod
    def prettify_ddl(ddl: dict, fancy=True) -> str:
        """
        Return a string that is a string version of the ddl, which can display to user
        :param ddl: a ddl to display
        :param fancy: if True, add a horizontal line above ddl
        :return: a string that is a pretty version of the ddl
        """
        if ddl is None:
            return "[Error] The ddl to parse is None."

        at_participant_user = ""
        for participant in ddl["participants"]:
            at_participant_user += f"[CQ:at,qq={participant}] "

        return ("===============\n" if fancy else "") + \
               f"日期: {ddl['date']}, 标题: {ddl['title']}\n" + \
               f"参与者: {at_participant_user}\n" + \
               f"备注: {ddl['description']}"

    @staticmethod
    # TODO: num_msg_group is not a good idea (especially passing None when we don't need group print), other solutions?
    def prettify_ddl_list(ddl_list: list, fancy=True, print_index=False, num_msggroup=None) -> str:
        """
        Prettify a list of ddl, use prettify_ddl to prettify each ddl
        :param ddl_list: a list of ddl to prettify
        :param fancy: if True, add a horizontal line above each ddl
        :param print_index: if True, add index before each ddl
        :param num_msggroup: used when print ddl in groups.
        :return: a string that is a pretty version of the list of ddl
        """
        if (ddl_list is None) or (not ddl_list):
            return "Hooray! You have no ddl."

        # The ddl in json is not sorted. We want to output them from the earliest to the latest.
        ddl_list.sort(key=lambda ddl_: ddl_["date"])

        result = ""
        for i in range(len(ddl_list)):
            result += (str(i + num_msggroup) if print_index else "") + DDLService.prettify_ddl(ddl_list[i],
                                                                                               fancy) + "\n"

        return result

    def process_query(self, query: list, user_qq: str) -> list:
        """
        This function processes queries from front-end, and return a string that is the result of the query
        :param query: a list that is the query from front-end, should be like "['ddl', 'today']"
        :param user_qq: the qq account of the user who perform the query
        :return: a string that is the result of the query to be displayed to user
        """
        toreturn = []
        if (query is None) or (not query):
            toreturn.append("[Internal Error] The query is empty.")
        if len(query) < 2:
            toreturn.append("[Error] Invalid syntax. Use \"ddl help\" to check usage.")

        if query[0] != "ddl":
            toreturn.append("[Internal Error] Non-ddl query should not be passed into function process_query.")

        # now, process queries
        q_type = query[1]  # query type
        if q_type == "today":
            toreturn.append("ddl due today: \n" +
                            DDLService.prettify_ddl_list(
                                self.get_ddl(lambda ddl: ddl["date"] == str(datetime.date.today()))
                            ))
        elif q_type == "tomorrow" or q_type == "tmr":
            toreturn.append("ddl due tomorrow: \n" +
                            DDLService.prettify_ddl_list(
                                self.get_ddl(lambda ddl: ddl["date"] == str(
                                    datetime.date.today() + datetime.timedelta(days=1)))
                            ))
        # search ddl for next week
        elif q_type == "week":
            toreturn.append("ddl due in a week: \n" +
                            DDLService.prettify_ddl_list(
                                self.get_ddl(lambda ddl:
                                             str(datetime.date.today() + datetime.timedelta(days=8))
                                             >= ddl["date"] >= str(datetime.date.today()))
                            ))
        # else if the q_type is a date
        elif re.search(r"^\d{4}-\d{2}-\d{2}$", q_type):
            toreturn.append("ddl due on " + q_type + ": \n" +
                            DDLService.prettify_ddl_list(self.get_ddl(
                                lambda ddl: ddl["date"] == str(datetime.datetime.strptime(q_type, "%Y-%m-%d").date()))
                            ))
        # search ddl for the user performed query
        elif q_type == "my":
            toreturn.append(f"ddl due in a week for [CQ:at,qq={user_qq}]: \n" +
                            DDLService.prettify_ddl_list(self.get_ddl(
                                lambda ddl: (str(user_qq) in ddl["participants"]) and
                                            str(datetime.date.today() + datetime.timedelta(days=8))
                                            >= ddl["date"] >= str(datetime.date.today()))
                            ))
        # syntax help
        elif q_type == "help":
            toreturn.append("[ddl today]: show ddl due today\n" +
                            "[ddl tomorrow][ddl tmr]: show ddl due tomorrow\n" +
                            "[ddl week]: show ddl due in a week\n" +
                            "[ddl <date>]: show ddl due on a certain date (format: \"yyyy-mm-dd\")\n" +
                            "[ddl my]: show ddl due in a week for you\n" + "[ddl insert]: insert a new ddl\n" +
                            "[ddl delete]: delete a ddl by its index\n" +
                            "[ddl help]: show this help")
        # insert a new ddl
        elif q_type == 'insert':
            if len(query) == 2:
                toreturn.append('ddl insert {"title": "insert your title here", "date": "insert your date here", '
                                '"participants": "at participants", "description": "insert your description here"}')
            else:
                ddl_info = ""
                for i in range(2, len(query)):
                    ddl_info += query[i] + " "
                print(ddl_info)
                try:
                    res = json.loads(ddl_info)
                    curr_date = res["date"]
                    participants_before = res["participants"]
                    # this regex can match all the qq numbers in the string
                    participants_after = re.findall(r"\[CQ:at,qq=(\d*)]", participants_before)
                    if not participants_after:
                        toreturn.append("[Error] Invalid Participants.")
                    res["participants"] = participants_after
                    if re.search(r"^\d{4}-\d{2}-\d{2}$", curr_date):
                        self.ddl_list.append(res)
                        self.store_ddl()
                        toreturn.append('Inserted successfully!')
                    else:
                        toreturn.append('[Error] Invalid Date.')
                except json.JSONDecodeError:
                    toreturn.append("[Error] Invalid syntax. Use \"ddl insert\" to check usage.")
        elif q_type == 'delete':
            if len(query) > 2:
                try:
                    index = int(query[2])
                    self.load_ddl_from_file()
                    if index not in range(len(self.ddl_list)):
                        toreturn.append("[Error] Index out of range.")
                    else:
                        del self.ddl_list[index]
                        self.store_ddl()
                        toreturn.append('Deleted successfully!')
                except ValueError:
                    toreturn.append('[Error] Invalid syntax. Use \"ddl delete\" to check usage.')
            else:
                ddls = '回复ddl delete <指定ddl编号> 来删除指定ddl哦\n'
                toreturn.append(ddls)
                for i in range(0, len(self.ddl_list), 2):
                    ddls = self.prettify_ddl_list(self.ddl_list[i:i + 2], print_index=True, num_msggroup=i) + '\n'
                    toreturn.append(ddls)
        else:
            toreturn.append("[Error] Invalid syntax. Use \"ddl help\" to check usage.")
        print(toreturn)
        return toreturn


if __name__ == "__main__":
    ddl_service = DDLService()

    # get today's ddl
    today = datetime.date.today()
    print(today)
    today_ddl = ddl_service.get_ddl(lambda ddl: ddl["date"] == str(today))  # remember to cast data to string
    print(today_ddl)

    # get tomorrow's ddl
    tomorrow = today + datetime.timedelta(days=1)
    print(tomorrow)
    tomorrow_ddl = ddl_service.get_ddl(lambda ddl: ddl["date"] == str(tomorrow))
    print(tomorrow_ddl)

    # test prettify_ddl
    print('\n' * 3)
    print(DDLService.prettify_ddl(tomorrow_ddl[0]))
    print(DDLService.prettify_ddl(tomorrow_ddl[1], fancy=True))

    # test prettify_ddl_list
    print('\n' * 3)
    print(DDLService.prettify_ddl_list(tomorrow_ddl, fancy=True))
    print('\n' * 3)
    print(DDLService.prettify_ddl_list(today_ddl, fancy=True))
