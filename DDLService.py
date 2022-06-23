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
    filename = "ddl.json"

    # Load ddl list from file, store the result in self.ddl_list
    with open(filename, "r") as f:
        ddl_list = json.load(f)  # A list of dict

    @staticmethod
    def get_ddl(predicate: lambda ddl: bool) -> list:
        """
        Return a list of ddl that satisfy the predicate
        :param predicate: a function that takes a ddl and returns True or False based on your predicate
        :return: a list of ddl that satisfy the predicate
        """
        return list(filter(predicate, DDLService.ddl_list))

    @staticmethod
    def store_ddl():
        """
        Store the self.ddl_list to file, we don't handle any exception here.
        """
        with open(DDLService.filename, "w") as f:
            json.dump(DDLService.ddl_list, f, indent=4, separators=(',', ': '))

    @staticmethod
    def remove_expired_ddl():
        """
        Remove all the expired ddl from self.ddl_list. This should be called periodically to
        tidy database.
        """
        DDLService.ddl_list = list(filter(lambda ddl: ddl['date'] >= str(datetime.date.today()), DDLService.ddl_list))
        DDLService.store_ddl()

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
    def prettify_ddl_list(ddl_list: list, fancy=True) -> str:
        """
        Prettify a list of ddl, use prettify_ddl to prettify each ddl
        :param ddl_list: a list of ddl to prettify
        :param fancy: if True, add a horizontal line above each ddl
        :return: a string that is a pretty version of the list of ddl
        """
        if (ddl_list is None) or (not ddl_list):
            return "Hooray! You have no ddl."

        # The ddl in json is not sorted. We want to output them from the earliest to the latest.
        ddl_list.sort(key=lambda ddl_: ddl_["date"])

        result = ""
        for ddl in ddl_list:
            result += DDLService.prettify_ddl(ddl, fancy) + "\n"

        return result
    @staticmethod
    def process_query(query: list, user_qq: str) -> str:
        """
        This function processes queries from front-end, and return a string that is the result of the query
        :param query: a list that is the query from front-end, should be like "['ddl', 'today']"
        :param user_qq: the qq account of the user who perform the query
        :return: a string that is the result of the query to be displayed to user
        """
        if (query is None) or (not query):
            return "[Internal Error] The query is empty."
        if len(query) < 2:
            return "[Error] Invalid syntax. Use \"ddl help\" to check usage."

        if query[0] != "ddl":
            return "[Internal Error] Non-ddl query should not be passed into function process_query."

        # now, process queries
        q_type = query[1]  # query type
        if q_type == "today":
            return "ddl due today: \n" + \
                   DDLService.prettify_ddl_list(DDLService.get_ddl(lambda ddl: ddl["date"] == str(datetime.date.today())))
        elif q_type == "tomorrow" or q_type == "tmr":
            return "ddl due tomorrow: \n" + \
                   DDLService.prettify_ddl_list(
                       DDLService.get_ddl(lambda ddl: ddl["date"] == str(datetime.date.today() + datetime.timedelta(days=1))))
        # search ddl for next week
        elif q_type == "week":
            return "ddl due in a week: \n" + \
                   DDLService.prettify_ddl_list(
                       DDLService.get_ddl(lambda ddl:
                                    str(datetime.date.today() + datetime.timedelta(days=8))
                                    >= ddl["date"] >= str(datetime.date.today()))
                   )
        # else if the q_type is a date
        elif re.search(r"^\d{4}-\d{2}-\d{2}$", q_type):
            return "ddl due on " + q_type + ": \n" + \
                   DDLService.prettify_ddl_list(DDLService.get_ddl(
                       lambda ddl: ddl["date"] == str(datetime.datetime.strptime(q_type, "%Y-%m-%d").date()))
                   )
        # search ddl for the user performed query
        elif q_type == "my":
            return f"ddl due in a week for [CQ:at,qq={user_qq}]: \n" + \
                   DDLService.prettify_ddl_list(DDLService.get_ddl(
                       lambda ddl: (str(user_qq) in ddl["participants"]) and
                                    str(datetime.date.today() + datetime.timedelta(days=8))
                                    >= ddl["date"] >= str(datetime.date.today()))
                   )
        # syntax help
        elif q_type == "help":
            return "[ddl today]: show ddl due today\n" + \
                   "[ddl tomorrow][ddl tmr]: show ddl due tomorrow\n" + \
                   "[ddl week]: show ddl due in a week\n" + \
                   "[ddl <date>]: show ddl due on a certain date (format: \"yyyy-mm-dd\")\n" + \
                   "[ddl my]: show ddl due in a week for you\n" + \
                   "[ddl insert]: insert a new ddl\n" + \
                   "[ddl help]: show this help"
        # insert a new ddl
        elif q_type == 'insert':
            if len(query) == 2:
                return 'ddl insert {"title": "insert your title here", "date": "insert your date here", ' \
                       '"participants": "at participants", "description": "insert your description here"}'
            ddl_info = ""
            for i in range(2, len(query)):
                ddl_info += query[i] + " "
            print(ddl_info)
            try:
                res = json.loads(ddl_info)
            except json.JSONDecodeError:
                return "[Error] Invalid syntax. Use \"ddl insert\" to check usage."
            curr_date = res["date"]
            participants_before = res["participants"]
            # this regex can match all the qq numbers in the string
            participants_after = re.findall(r"\[CQ:at,qq=(\d*)]", participants_before)
            if not participants_after:
                return "[Error] Invalid Participants."
            res["participants"] = participants_after
            if re.search(r"^\d{4}-\d{2}-\d{2}$", curr_date):
                DDLService.ddl_list.append(res)
                DDLService.store_ddl()
                return 'Inserted successfully!'
            else:
                return '[Error] Invalid Date.'
        else:
            return "[Error] Invalid syntax. Use \"ddl help\" to check usage."


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
