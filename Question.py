"""
all Questions should appear like :

{
      "name": "978. 最长湍流子数组",
      "id": "longest-turbulent-subarray",
      "link": "https://leetcode-cn.com/problems/longest-turbulent-subarray/",
      "difficulty": "中等",
      "description": "dp",
      "participants": ["enor2017"]
},

"""
from json import JSONEncoder

class Question:
    def __init__(self, problem_id: str, problem_description: str,
                 problem_name: str = None,  problem_link: str = None,
                 problem_difficulty: str = None, participants: list = []):
        """
        This constructor is used to init a question. Some fields are optional, if
        not provided, it can automatically fetch them from Leetcode API.
        :param problem_id: The unique problem id of question
        :param problem_description: The description (tags) of the problem, usually manually defined
        :param problem_name: (Optional) The name of the problem
        :param problem_link: (Optional) The link of the problem
        :param problem_difficulty: (Optional) The difficulty of the problem
        :param participants: (Optional) The list of participants who have solved the problem, if not provided,
        it will init an empty list.
        :exception: ValueError if the problem_id is not valid
        """
        self.id = problem_id
        self.description = problem_description
        self.participants = participants
        # if all details have been provided, we don't need to get from leetcode website
        if problem_name is not None and problem_link is not None and problem_difficulty is not None:
            self.name = problem_name
            self.link = problem_link
            self.difficulty = problem_difficulty
            return
        details = Leetcode.get_prob_detail_from_id(problem_id)
        if not details:
            raise ValueError(f"Cannot find problem whose id is: {problem_id}.")
        self.name = details["name"] if problem_name is None else problem_name
        self.link = details["link"] if problem_link is None else problem_link
        self.difficulty = details["difficulty"] if problem_difficulty is None else problem_difficulty

    def __str__(self) -> str:
        return f"""
        题目名称: {self.name}
        题目链接: {self.link}
        题目难度: {self.difficulty}
        题目表填: {self.description}
        已完成的参与者: {self.participants}
        """


class QuestionEncoder(JSONEncoder):
    """
    This class is used to encode (serialize) a question object to json format.
    """
    def default(self, obj):
        return obj.__dict__
