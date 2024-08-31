from metagpt.roles.role import Role
from metagpt.actions import UserRequirement
from .Action.DescribeRequirements import DescribeRequirements

class Analyzer(Role):
    """
    业务分析师，根据用户的需求分析工控的实现逻辑，按条理逐步梳理清楚，需要由用户澄清模糊的地方。
    """
    name: str = "Bob"
    profile: str = "程序分析设计专家"
    goal: str = "快速有效的根据用户描述对客户需求，包含输入变量、输出变量和控制逻辑进行梳理，给出条理清晰的说明指导PLC控制代码的编写。"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([DescribeRequirements])