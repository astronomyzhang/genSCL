from metagpt.roles.role import Role
from .Action.WriteCode import WriteCode
from .Action.WriteTestcases import WriteTestcases
from .Action.DescribeRequirements import DescribeRequirements
from metagpt.actions import UserRequirement
from metagpt.schema import Message
from metagpt.logs import logger

class Tester(Role):
    """
    在接收到代码后设计代码的测试用例，保障代码可以完成用户需求。
    """
    name: str = "Cathy"
    profile: str = "程序测试专家，擅长根据业务分析师的规划和已生成的代码给出对控制逻辑覆盖全面的测试用例。"
    goal: str = "给出控制逻辑覆盖完整、可运行无bug的测试用例。"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteTestcases])
        self._watch([UserRequirement, DescribeRequirements])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        user_requirement = self.rc.memory.get_by_action(UserRequirement)
        plan = self.rc.memory.get_by_action(DescribeRequirements)[-1]

        testcase = await todo.run(user_requirement, plan)

        msg = Message(content=testcase, role=self.profile, cause_by=type(todo))
        return msg