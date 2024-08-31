from flask import Flask, request, jsonify
import time
import asyncio
from metagpt.team import Team
from Role.Analyzer import Analyzer
from Role.SCLCoder import SCLCoder
from Role.Tester import Tester
import os
import shutil
import json

app = Flask(__name__)

async def aigc(data: dict, outputPath: str):
    # 如果输出路径下已存在生成文件则删除对应文件。
    if os.path.isfile(outputPath):
        os.remove(outputPath)
    with open(outputPath, 'w', encoding='utf-8') as file:
        pass
    
    team = Team()
    team.hire(
        [
            Analyzer(),
            Tester(),
            SCLCoder(),
        ]
    )

    team.invest(investment=3.0)
    team.run_project(json.dumps(data, indent=4))
    try:
        await asyncio.wait_for(team.run(n_round=1), timeout=85)
    except asyncio.TimeoutError:
        filename = "./codetemplate/" + data["type"].upper() + "-to.txt"
        with open(filename, 'r', encoding='utf-8') as file:
            template = file.read()
        if data['type'] == 'FUNCTION':
            if "return_value" in data:
                template=template.format(name=data["name"], returntype=data["return_value"][0]["type"])
            else:
                template=template.format(name=data["name"], returntype="Void")
        else:
            template=template.format(name=data["name"])
        
        content = "\n { S7_Optimized_Access := 'TRUE' } \n"
        if "input" in data.keys():
            content += "VAR_INPUT\n"
            for item in data['input']:
                if "STRUCT" in item['type'].upper():
                    content += "   " + item["name"] + ":" + item["type"].upper() + "\n"
                    for structitem in item["fields"]:
                        content += "      " + structitem["name"] + ":" + structitem["type"].upper() + ";\n"
                    content += "   END_STRUCT;\n"
                else:
                    content += "   " + item["name"] + ":" + item["type"].upper() + ";\n"
            content += "END_VAR\n"

        if "output" in data.keys():
            content += "VAR_OUTPUT\n"
            for item in data['output']:
                if "STRUCT" in item['type'].upper():
                    content += "   " + item["name"] + ":" + item["type"].upper() + "\n"
                    for structitem in item["fields"]:
                        content += "      " + structitem["name"] + ":" + structitem["type"].upper() + ";\n"
                    content += "   END_STRUCT;\n"
                else:
                    content += "   " + item["name"] + ":" + item["type"].upper() + ";\n"
            content += "END_VAR\n"

        if "in/out" in data.keys():
            content += "VAR_IN_OUT\n"
            for item in data['in/out']:
                if "STRUCT" in item['type'].upper():
                    content += "   " + item["name"] + ":" + item["type"].upper() + "\n"
                    if type(item["fields"]) == list:
                        for structitem in item["fields"]:
                            content += "      " + structitem["name"] + ":" + structitem["type"].upper() + ";\n"
                    content += "   END_STRUCT;\n"
                else:
                    content += "   " + item["name"] + ":" + item["type"].upper() + ";\n"
            content += "END_VAR\n"

        content += "BEGIN\n\n"
        content += "END_" + data["type"].upper()
        template += content

        if os.path.isfile(outputPath):
            os.remove(outputPath)
        with open(outputPath, 'w', encoding='utf-8') as f:
            f.write(template)


@app.route('/', methods=['POST'])
def generate_code():
    data = request.get_json()

    inputDir = "./input"
    inputName = data.get("name") + ".json"
    inputPath = os.path.join(inputDir, inputName)
    if os.path.isfile(inputPath):
        os.remove(inputPath)
    with open(inputPath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

    outputDir = "./output"
    fileName = data.get("name") + ".scl"
    outputPath = os.path.join(outputDir, fileName) 
    
    start_time = time.time()
    asyncio.run(aigc(data, outputPath))
    with open(outputPath, 'r', encoding='utf-8') as file:
        code = file.read()
    response = {
        "name": data.get("name"),
        "code": code
    }
    end_time = time.time()
    print("程序总耗时：" + str(end_time-start_time))
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)