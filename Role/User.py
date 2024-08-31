from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.actions import UserRequirement
from .Action.ProvideInformation import ProvideInformation
from .Action.DescribeRequirements import DescribeRequirements

class User(Role):
    name: str = "Garwen"
    profile: str = "用户"
    goal:str = "提供程序设计专家需要的所有信息使其对需求做到绝对清晰无歧义。"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ProvideInformation])
        self._watch([DescribeRequirements, UserRequirement])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories()

        clarification = await todo.run(context)
        msg = Message(content=clarification, role=self.profile, cause_by=type(todo))

        return msg