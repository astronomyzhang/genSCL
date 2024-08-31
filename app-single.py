from flask import Flask, request, jsonify
import time
import asyncio
from metagpt.team import Team
from Role.Analyzer import Analyzer
from Role.SCLCoderSingle import SCLCoderSingle
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
            SCLCoderSingle(),
        ]
    )

    team.invest(investment=3.0)
    team.run_project(json.dumps(data, indent=4))

    try:
        await asyncio.wait_for(team.run(n_round=1), timeout=85)
    except asyncio.TimeoutError:
        print("执行已超时，在这里执行格式化的原始codetemplate")
        
        filename = "./codetemplate/" + data["type"] + ".txt"
        with open(filename, 'r', encoding='utf-8') as file:
            template = file.read()
        if data['type'] == 'FUNCTION':
            if "return_value" in data:
                template=template.format(name=data["name"], returntype=data["return_value"][0]["type"])
            else:
                template=template.format(name=data["name"], returntype="Void")
        else:
            template=template.format(name=data["name"])

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