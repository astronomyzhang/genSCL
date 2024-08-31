from metagpt.actions.action import Action
import json
from metagpt.schema import CodingContext, Document
from metagpt.logs import logger
from pydantic import Field
import os
import re

def findname(directory: str):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return file.split('.')[0]
    return None

def file_write(directory: str, response: str, dataType:str):
    if dataType == "FUNCTION_BLOCK":
        start_tag = "FUNCTION_BLOCK \""
        end_tag = "END_FUNCTION_BLOCK"
    else:
        start_tag = "FUNCTION \""
        end_tag = "END_FUNCTION"
        
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
    if "END_FUNCTION;" in response:
        response = response.replace("END_FUNCTION;", "END_FUNCTION")
    if "END_VAR;" in response:
        response = response.replace("END_VAR;", "END_VAR")
    if "END_REGION;" in response:
        response = response.replace("END_REGION;", "END_REGION")
    if "DIV" in response:
        response = response.replace("DIV", "/")
    if "ELSEIF" in response:
        response = response.replace("ELSEIF", "ELSIF")
    pattern = r'END_IF(?!;)'
    if(re.search(pattern, response)):
        # 替换为 END_IF;
        response = re.sub(pattern, 'END_IF;', response)
    
    pattern = r'END_FOR(?!;)'
    if(re.search(pattern, response)):
        response = re.sub(pattern, 'END_FOR;', response)

    pattern = r'END_WHILE(?!;)'
    if(re.search(pattern, response)):
        response = re.sub(pattern, 'END_WHILE;', response)

    pattern = r'END_REPEAT(?!;)'
    if(re.search(pattern, response)):
        response = re.sub(pattern, 'END_REPEAT;', response)

    pattern = r'CONTINUE(?!;)'
    if(re.search(pattern, response)):
        response = re.sub(pattern, 'CONTINUE;', response)

    pattern = r'EXIT(?!;)'
    if(re.search(pattern, response)):
        response = re.sub(pattern, 'EXIT;', response)
    
    # 定义正则表达式模式
    pattern = r"DOWNTO (\S+)"
    # 定义替换字符串
    replacement = r"TO \1 BY -1"
    if(re.search(pattern, response)):
        response = re.sub(pattern, replacement, response)

    return response

class WriteCodeSingle(Action):
    PROMPT_TEMPLATE:str = """
    【任务描述开始】
    请根据用户的需求内容结合Legacy Code中的代码说明，逐步分析任务内容，写出可以在TIA PORTAL V19上运行的SCL程序。
    重要提示：仅给出完整的程序即可不需要写出分析过程，所生成内容不能有省略或者伪代码。
    重要提示：请从Example中学习SCL程序的结构和语法知识，参考其格式和内容进行代码生成。
    重要提示：不要省略或概括规划中的任何内容。
    重要提示：代码应具备较高的执行效率。
    重要提示：保障程序的可阅读性和可维护性，要求代码清晰简洁。
    重要提示：代码对规划中的内容必须完全覆盖，程序整体结构完整可运行。
    重要提示：代码以“START_SCL”开头，以“END_SCL”结尾。
    重要提示：请学习Legacy Code中的内容，你仅可以替换```和```中间的内容，其他地方不可改动。
    重要提示：不要让用户为你补充代码，你必须提供完整的可执行的代码。
    重要提示：请记住生成的代码应符合Siemens SCL语言规范,不要出现SCL语言的编程语法错误。。

    重要提示：程序中的所有变量都必须先声明后才能使用，不可在程序中使用未经声明的变量.
    重要提示：变量的声明和初始化请严格按照Legacy Code中的要求执行。
    重要提示：FOR循环的运行变量取值边界不可使用数组直接取值。
    重要提示：请勿使用任何函数，使用变量和基础的顺序、判断和循环逻辑完成任务。
    重要提示：请不要在代码中写注释。

    【任务描述结束】

    【Example Start】
    {examples}
    【Example End】
    
    【Context Start】
    # UserRequirement
    {user_requirement}

    # Legacy Code
    {template}
    【Context End】
    
    【SCL_START】
    SCL语言代码在此处生成
    【SCL_END】
    """
    
    name: str = "WriteCode"
    directory: str = "./output"
    examplePath: str = './sample/Examples.txt'

    async def run(self, user_requirement: str):
        print(user_requirement)
        casename = findname(self.directory)
        inputPath = "./input/" + casename + ".json"
        
        with open(inputPath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        filename = "./codetemplate/" + data["type"] + ".txt"
        with open(filename, 'r', encoding='utf-8') as file:
            template = file.read()

        with open(self.examplePath, 'r', encoding='utf-8') as file:
            examples = file.read()

        if data['type'] == 'FUNCTION':
            if "return_value" in data:
                template=template.format(name=data["name"], returntype=data["return_value"][0]["type"])
            else:
                template=template.format(name=data["name"], returntype="Void")
        else:
            template=template.format(name=data["name"])

        prompt = self.PROMPT_TEMPLATE.format(
            template=template,
            user_requirement = user_requirement,
            examples = examples,
        )
        rsp = await self._aask(prompt)
        rsp = process(rsp)

        file_write(self.directory, rsp, data["type"])
        return rsp