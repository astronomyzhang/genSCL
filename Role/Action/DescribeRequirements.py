from metagpt.actions.action import Action

class DescribeRequirements(Action):
    """
    用户将提供工厂控制任务说明和需求控制逻辑的自然语言描述。如果描述有歧义的地方，请按照最通俗符合大众的角度进行理解，根据理解信息生成规划内容。
    """
    PROMPT_TEMPLATE: str = r"""
    【任务描述开始】
    请根据用户提供的{instruction}进行拆解归纳为函数块名称、程序类型和控制逻辑。控制逻辑中需要根据原始信息进行归纳总结，按条理清晰的逻辑逐项归纳说明，每一条以换行符结尾。不要输出任何代码信息。

    重要提示：不要做任何假设。
    重要提示：在进行规划时不需要考虑PLC硬件相关内容，你所规划的内容应与所运行的PLC硬件型号解耦。
    重要提示：请勿添加、修改或删除任何用户反馈的信息。
    重要提示：以“【规划开始】”开始描述你的规划，以“【规划结束】”结束你的规划描述。
    重要提示：请根据有限状态机的设计进行规划，在规划中可以清楚地解释每个状态和输入、输出变量。
    重要提示：当用户表述中存在复位操作时，则应在复位操作后立刻将所有输入、输出变量重置为默认值。
    【任务描述结束】
    
    【示例_规划开始】
    ```示例_规划内容```
    【示例_规划结束】
    """
    name: str = "DescribeRequirements"

    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)

        rsp = await self._aask(prompt)

        return rsp