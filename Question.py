"""
all Questions should appear like :

{
    "2022/03/01": {
        "problem_name": "1. 两数之和",
        "problem_id": "two_sum",
        "problem_link": "https://....",
        "problem_difficulty": "简单",
        "problem_description": "哈希表，二分查找",
        "participants": "enor2017"
    }
}

"""


class Question:
    def __init__(self, problem_date: str, problem_name: str, problem_id: str, problem_link: str,
                 problem_diifficulty: str, problem_description: str, participants: dict):
        self.date = problem_date
        self.name = problem_name
        self.id = problem_id
        self.link = problem_link
        self.difficulty = problem_diifficulty
        self.description = problem_description
        self.participants = participants

    def getDate(self) -> str:
        return self.date

    def getName(self) -> str:
        return self.name

    def getId(self) -> str:
        return self.id

    def getLink(self) -> str:
        return self.link

    def getDifficulty(self) -> str:
        return self.difficulty

    def getDescription(self) -> str:
        return self.description

    def getParticipants(self) -> dict:
        return self.participants

    def toString(self) -> str:
        result = self.date + ":\n" + "今日题目 : " + self.name + "\n" + \
                 "题目链接 : " + self.link + "\n" + \
                 "难度 : " + self.difficulty + "\n" + \
                 "标签 : " + self.description + "\n"
