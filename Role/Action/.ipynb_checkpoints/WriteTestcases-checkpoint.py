from metagpt.actions.action import Action
from tenacity import retry, stop_after_attempt, wait_random_exponential
import os

class WriteTestcases(Action):
    PROMPT_TEMPLATE: str = """
    【任务描述开始】
    请根据给出规划内容生成不少于控制逻辑数量的测试用例。
    重要提示：测试用例需要总结为表格，包含序号、内容、前置条件、输入、预期输出。
    重要提示：在每一条测试用例中需要包含所有输入和输出变量。
    【任务描述结束】

    【Context Start】
    # UserRequirement
    {user_requirement}
    
    # Planning
    {plan}
    【Context End】

    【Testcase Start】
    ```测试用例在此处生成```
    【Testcase End】
    """
    name: str = "WriteTestCases"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def write_case(self, prompt) -> str:
        case_rsp = await self._aask(prompt)
        return case_rsp
    
    async def run(self, user_requirement: str, plan: str):
        prompt = self.PROMPT_TEMPLATE.format(
            user_requirement=user_requirement,
            plan = plan,
        )
        rsp = await self.write_case(prompt)

        return rsp