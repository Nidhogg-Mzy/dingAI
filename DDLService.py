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
    "description": "2PM - 4PM. Join at 1PM for attendance checking.\nZoom link: https://course.cse.ust.hk/comp2211/midterm-zoom-meeting.html"
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
        ddl_list.sort(key=lambda ddl: ddl["date"])

        result = ""
        for ddl in ddl_list:
            result += DDLService.prettify_ddl(ddl, fancy) + "\n"

        return result

    def process_query(self, query: list, user_qq: str) -> str:
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
                   DDLService.prettify_ddl_list(self.get_ddl(lambda ddl: ddl["date"] == str(datetime.date.today())))
        elif q_type == "tomorrow" or q_type == "tmr":
            return "ddl due tomorrow: \n" + \
                   DDLService.prettify_ddl_list(
                       self.get_ddl(lambda ddl: ddl["date"] == str(datetime.date.today() + datetime.timedelta(days=1))))
        # search ddl for next week
        elif q_type == "week":
            return "ddl due in a week: \n" + \
                   DDLService.prettify_ddl_list(
                       self.get_ddl(lambda ddl: ddl["date"] <= str(datetime.date.today() + datetime.timedelta(days=8))))
        # else if the q_type is a date
        elif re.search(r"^\d{4}-\d{2}-\d{2}$", q_type):
            return "ddl due on " + q_type + ": \n" + \
                   DDLService.prettify_ddl_list(self.get_ddl(
                       lambda ddl: ddl["date"] == str(datetime.datetime.strptime(q_type, "%Y-%m-%d").date()))
                   )
        # search ddl for the user performed query
        elif q_type == "my":
            return f"ddl due in a week for [CQ:at,qq={user_qq}]: \n" + \
                   DDLService.prettify_ddl_list(self.get_ddl(
                       lambda ddl: (str(user_qq) in ddl["participants"]) and
                                   (ddl["date"] <= str(datetime.date.today() + datetime.timedelta(days=8))))
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
            currDate = res["date"]
            participantsBefore = res["participants"]
            parts = participantsBefore.split(' ')
            participantsAfter = []
            for part in parts:
                if len(part) < 5:
                    continue
                match = re.findall(r"^\[CQ:at,qq=(\d*)\]$", part)
                participantsAfter.append(match[0])
            if not participantsAfter:
                return "[Error] Invalid Participants."
            res["participants"] = participantsAfter
            if re.search(r"^\d{4}-\d{2}-\d{2}$", currDate):
                self.ddl_list.append(res)
                with open(self.filename, 'w') as f:
                    json.dump(self.ddl_list, f, indent=4, separators=(',', ': '))
                return 'inserted successfully'
            else:
                return '[Error] Invalid Date.'
        else:
            return "[Error] Invalid syntax. Use \"ddl help\" to check usage."

    def add_ddl(self, ddl: dict) -> bool:
        """
        Add a ddl to the database
        :param ddl: a dict that is the ddl to be added
        :return: True if the ddl is added successfully, False otherwise
        """
        if (ddl is None) or (not ddl):
            return False

        # check if the ddl is valid
        if not self.is_ddl_valid(ddl):
            return False

        # check if the ddl already exists
        if self.get_ddl(lambda d: ddl["date"] == d["date"] and ddl["title"] == d["title"]):
            return False

        # add the ddl to the database
        self.ddl_list.append(ddl)
        self.save_ddl_list()

        return True


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
