from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.actions import UserRequirement

from .Action.DescribeRequirements import DescribeRequirements
from .Action.WriteCode import WriteCode
from .Action.WriteTestcases import WriteTestcases

class SCLCoder(Role):
    """
    通过业务分析师分析出的PRD文档，给出工业控制逻辑的SCL代码实现。
    """
    name:str = "Jack"
    profile: str = "编写工业控制程序的专家，擅长采用编写逻辑思路清晰、没有bug可直接编译运行的SCL语言程序。"
    goal: str = "根据客户反馈的信息和业务分析师给出的规划，写出逻辑思路清晰、没有bug、可以直接在TIA PORTAL V19上运行的SCL程序。"
    constraints: str = (
        "必须使用SCL语言"
        "所有代码严格遵守西门子SCL语言规范要求"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([DescribeRequirements, UserRequirement, WriteTestcases])
        self.set_actions([WriteCode])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        user_requirement = self.rc.memory.get_by_action(UserRequirement)
        plan = self.rc.memory.get_by_action(DescribeRequirements)
        testcase = self.rc.memory.get_by_action(WriteTestcases)

        code = await todo.run(user_requirement, plan, testcase)

        msg = Message(content=code, role=self.profile, cause_by=type(todo))
        return msg