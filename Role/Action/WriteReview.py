from metagpt.actions.action import Action
import os
import re

def file_write(directory: str, response: str):
    start_tag = "FUNCTION_BLOCK"
    end_tag = "END_FUNCTION_BLOCK"
    
    start_index = response.find(start_tag)
    end_index = response.find(end_tag)
    content = response[start_index :end_index+ len(end_tag)].strip()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    return None

def process(response: str):
    if "END_FUNCTION_BLOCK;" in response:
        response = response.replace("END_FUNCTION_BLOCK;", "END_FUNCTION_BLOCK")
    if "END_VAR;" in response:
        response = response.replace("END_VAR;", "END_VAR")
    if "DIV" in response:
        response = response.replace("DIV", "/")
    pattern = r'(?<!\S)END_IF(?!\S)'
    if(re.search(pattern, response)):
        # 替换为 END_IF;
        response = re.sub(pattern, 'END_IF;', response)
    
    pattern = r'(?<!\S)END_FOR(?!\S)'
    if(re.search(pattern, response)):
        # 替换为 END_IF;
        response = re.sub(pattern, 'END_FOR;', response)
    
    # 定义正则表达式模式
    pattern = r"DOWNTO (\S+)"
    # 定义替换字符串
    replacement = r"TO \1 BY -1"
    if(re.search(pattern, response)):
        # 替换为 END_IF;
        response = re.sub(pattern, replacement, response)

    return response

class WriteReview(Action):
    PROMPT_TEMPLATE: str = """
    【任务描述开始】
    请你认真研读用户需求、规划、测试用例和多位程序专家给出的代码，给出你认为最能满足客户需求的SCL语言程序。
    【任务描述结束】

    【Context Start】
    # UserRequirement
    {user_requirement}
    
    # Planning
    {plan}

    # Testcases
    {testcase}
    【Context End】

    【Candidate Start】
    {competitor}
    【Candidate End】

    【SCL_START】
    ```在此处给出你的SCL程序```
    【SCL_END】
    """
    name: str = "WriteReview"
    directory: str = "./output"

    async def run(self, user_requirement: str, plan: str, testcase: str, competitor: str):
        prompt = self.PROMPT_TEMPLATE.format(
            user_requirement = user_requirement,
            plan = plan,
            testcase = testcase,
            competitor = competitor,
        )
        rsp = await self._aask(prompt)
        rsp = process(rsp)
        file_write(self.directory, rsp)
        return rsp