from dataclasses import field
import os
from pydoc import describe
from tkinter import Image
from flask import Flask, request, jsonify, abort, render_template, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from dotenv import load_dotenv
import base64
from PIL import Image
import io
from google import genai
from google.genai import types
from pydantic import BaseModel
from load_output_format import *
import json
import ipaddress
from typing import Callable


# --- 自定义密钥函数 ---
def get_ip_subnet(subnet_mask: int = 24) -> Callable[[], str]:
    """
    这是一个工厂函数, 它返回一个根据指定子网掩码生成key的函数。
    这使得我们可以轻松地配置不同的子网大小，例如 /24 for IPv4 或 /64 for IPv6。
    """
    def key_func() -> str:
        if hasattr(g, 'userOwnKey') and g.userOwnKey is True:
            return None

        # 1. 获取请求的原始IP地址
        ip_str = request.headers.get('X-Real-IP', request.remote_addr)

        try:
            # 2. 将IP字符串解析为ipaddress对象，并附加上子网掩码
            #    ipaddress模块能自动处理IPv4和IPv6
            interface = ipaddress.ip_interface(f"{ip_str}/{subnet_mask}")
            
            # 3. 返回该IP所属的网络地址字符串作为Key
            #    例如，对于IP '192.168.1.100' 和掩码 24, 这将返回 '192.168.1.0/24'
            return str(interface.network)
        except ValueError:
            # 如果get_remote_address()返回的不是一个有效的IP地址，则直接返回原始值
            return ip_str
            
    return key_func

# 加载环境变量
load_dotenv()

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 设置工作目录为脚本所在目录
os.chdir(script_dir)

app = Flask(__name__)
# 初始化 Limiter
# 1. key_func=get_remote_address: 指定使用访问者的 IP 地址作为唯一标识。
# 2. storage_uri="redis://localhost:6379": 指定使用 Redis 存储访问数据。
#    如果 Redis 在不同主机或有密码，请相应修改，例如 "redis://:password@host:port"
# 3. default_limits:可以设置全局的默认限制（可选）
subnet_key_func = get_ip_subnet(subnet_mask=24)

limiter = Limiter(
    app=app,
    # 关键在这里：使用我们自定义的函数作为 key_func
    key_func=subnet_key_func,
    storage_uri="redis://127.0.0.1:6379/0",
    default_limits=["10000 per day", "10000 per hour"]
)

# 允许来自 http://localhost:5173 (Vue 开发服务器默认地址) 的跨域请求
# CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5173"}})
CORS(app, resources={r"/api/*": {"origins": "https://www.nepfuns.xyz"}})

# 处理图片格式
def process_image(image_file):
    # 使用 Pillow 确保图片是 JPEG 格式
    img = Image.open(image_file.stream)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    buffered.seek(0)

    return Image.open(buffered)

def get_prompt(config_path: str, prompt_type: str, lang:str) -> str:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config.get('prompts', {}).get(prompt_type, {}).get(lang)

def get_form(config_path: str, form_type: str) -> dict:
    # 使用 'with' 语句安全地打开和读取文件
    with open(config_path, 'r', encoding='utf-8') as f:
        # 使用 yaml.safe_load() 解析 YAML 内容
        config = yaml.safe_load(f)
    return config.get('types', {}).get(form_type).get('fields', {})

# 处理所有其他路由，将它们指向 Vue 应用
# 这样，Vue Router 就能接管前端路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # 如果请求的是 API 路由，则不会被这个路由捕获
    if path != "" and path.startswith('api/'):
         return "Not Found", 404
    # 对于所有非 API、非静态文件的请求，都返回前端的 index.html
    return render_template("index.html")

@app.before_request
def check_api_type():
    if 'apiSettings[useOwnKey]' in request.form and request.form['apiSettings[useOwnKey]'] == 'true':
        g.userOwnKey = True
    else:
        g.userOwnKey = False

@app.route('/api/generate', methods=['POST'])
@limiter.limit("5/day")
def generate_text():
    # 1. 检查文件和表单数据是否存在
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    if 'user_settings' not in request.form:
        return jsonify({'error': 'No settings part'}), 400
    if 'used_type' not in request.form:
        return jsonify({'error': 'No settings part'}), 400

    image_file = request.files['image']
    user_settings = request.form['user_settings']
    used_type = request.form['used_type']
    lang = request.form['lang']

    # 2. 处理图片
    try:
        user_image = process_image(image_file)
    except Exception as e:
        return jsonify({"error": f"Image processing failed: {e}"}), 500

    # 3. 结合预设 Prompt，构造发送给 LLM 的数据
    try:
        preset_prompt = get_prompt(os.getenv('PRESET_PROMPT_CONFIG_FILE_PATH'), used_type, lang)
        user_prompt = get_prompt(os.getenv('USER_PROMPT_CONFIG_FILE_PATH'), used_type, lang).format(**request.form) + '\n' + user_settings
    except Exception as e:
        return jsonify({"error": f"fail to load a prompt from yaml: {e}"}), 400

    # 4.调用LLM API
    # 获取输出格式
    dynamic_models = load_models_from_config(os.getenv('OUTPUT_CONFIG_FILE_PATH'))
    if used_type not in dynamic_models:
        return jsonify({'error': 'No ouput format provided'}), 400

    if os.getenv('LLM_MODEL') == "gemini":
        api_key=os.getenv('API_KEY_DEFAULT')
        if 'apiSettings[useOwnKey]' in request.form and request.form['apiSettings[useOwnKey]'] == 'true':
            api_key = request.form['apiSettings[apiKey]'].strip()
        if api_key == '':
            return jsonify({"error": "invalid app key"}), 400
        gemini_client = genai.Client(api_key=api_key)
        gemini_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=-1,
            ),
            system_instruction=preset_prompt,
            response_mime_type='application/json',
            response_schema=list[dynamic_models[used_type]]
        )
        contents = [user_image, user_prompt]
        try:
            response = gemini_client.models.generate_content(
                model=os.getenv('GEMINI_MODEL'),
                contents=contents,
                config=gemini_config
            )
        except genai.errors.ClientError as e:
            return jsonify({"error": e.response.text}), 400
            

        return jsonify(json.loads(response.text)[0])

    else:
        return jsonify({"error": "Not supported model"}), 400

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "The request limit has been reached. You can continue by using a custom API key."}), 429
    # return jsonify(error="ratelimit exceeded", message="The request limit has been reached. You can continue by using a custom API key."), 429


@app.route('/api/get-form-config', methods=['GET'])
def get_form_config():
    """
    一个 API 端点，用于读取 YAML 文件，将其解析为 Python 字典，
    然后以 JSON 格式返回给前端。
    """
    try:
        # 使用 'with' 语句安全地打开和读取文件
        with open(os.getenv('INPUT_CONFIG_FILE_PATH'), 'r', encoding='utf-8') as f:
            # 使用 yaml.safe_load() 解析 YAML 内容
            yaml_data :dict = yaml.safe_load(f)
        for (key, value) in yaml_data['types'].items():
            if 'fields' in yaml_data['types'][key]:
                for sub_field in yaml_data['types'][key]['fields'].values():
                    if 'label-zh' in sub_field and type(sub_field['label-zh']) is str:
                        pass
                    else:
                        return jsonify({"error": f"Input setting file has wrong format"}), 400
            # else:
            #     return jsonify({"error": f"Input setting file has wrong format"}), 400

        # 使用 jsonify 将 Python 字典转换为 JSON 响应
        return jsonify(yaml_data)

    except FileNotFoundError:
        # 如果文件不存在，返回 404 错误
        print(f"错误: 配置文件未找到于路径 {os.getenv('INPUT_CONFIG_FILE_PATH')}")
        return jsonify({"error": f"No setting file found: {e}"}), 400
    except Exception as e:
        # 处理其他可能的错误 (例如 YAML 格式错误)
        print(f"错误: 处理文件时发生错误: {e}")
        return jsonify({"error": f"Process setting file error: {e}"}), 500

@app.route('/api/get-output-config', methods=['GET'])
def get_output_config():
    """
    一个 API 端点，用于读取 YAML 文件，将其解析为 Python 字典，
    然后以 JSON 格式返回给前端。
    """
    try:
        # 使用 'with' 语句安全地打开和读取文件
        with open(os.getenv('OUTPUT_CONFIG_FILE_PATH'), 'r', encoding='utf-8') as f:
            # 使用 yaml.safe_load() 解析 YAML 内容
            yaml_data :dict = yaml.safe_load(f)
        for (key, value) in yaml_data['types'].items():
            if 'fields' in yaml_data['types'][key]:
                for sub_field in yaml_data['types'][key]['fields'].values():
                    if 'label-zh' in sub_field and type(sub_field['label-zh']) is str:
                        pass
                    else:
                        return jsonify({"error": f"Input setting file has wrong format"}), 400
            else:
                return jsonify({"error": f"Input setting file has wrong format"}), 400

        # 使用 jsonify 将 Python 字典转换为 JSON 响应
        return jsonify(yaml_data)

    except FileNotFoundError:
        # 如果文件不存在，返回 404 错误
        print(f"错误: 配置文件未找到于路径 {os.getenv('INPUT_CONFIG_FILE_PATH')}")
        return jsonify({"error": f"No setting file found: {e}"}), 400
    except Exception as e:
        # 处理其他可能的错误 (例如 YAML 格式错误)
        print(f"错误: 处理文件时发生错误: {e}")
        return jsonify({"error": f"Process setting file error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
