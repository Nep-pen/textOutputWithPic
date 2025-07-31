import os
import yaml
import pydantic
from pydantic import BaseModel, create_model, EmailStr
from typing import Any, Type, Optional, List, Dict

'''
注意: 此文件中model并非网络模型, 而是数据模型, 类似实体类
'''
def get_type_from_string(type_str: str) -> Type[Any]:
    """
    将字符串表示的类型转换为实际的Python类型对象。
    这是一个简化的实现，为了安全，它只从一个受信任的命名空间查找类型。
    
    Args:
        type_str: 类型字符串，例如 "str", "list[str]", "pydantic.EmailStr"

    Returns:
        实际的类型对象，例如 str, list[str], pydantic.EmailStr
    
    Raises:
        NameError: 如果找不到类型。
    """
    # 建立一个安全的、允许的类型查找范围
    # 包括了 builtins, typing模块, 和 pydantic
    allowed_scope = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': List,
        'dict': Dict,
        'Optional': Optional,
        'Any': Any,
        # Pydantic 特殊类型
        'BaseModel': BaseModel,
        'EmailStr': EmailStr,
        # 为了兼容 list[str] 这种写法, 我们需要 `List`
        'List': List, 
    }

    if '.' in type_str:
        # 处理 "pydantic.EmailStr" 这种情况
        module_name, type_name = type_str.rsplit('.', 1)
        if module_name == 'pydantic':
             return getattr(pydantic, type_name)
        # 可以根据需要扩展其他模块
        else:
            raise NameError(f"Module '{module_name}' is not supported in type strings.")

    # 使用 `eval`，但限制其上下文（globals），使其只能访问我们允许的类型
    # 这是一种相对安全的 eval 使用方式
    return eval(type_str, allowed_scope)

def load_models_from_config(config_path: str) -> Dict[str, Type[BaseModel]]:
    """
    从YAML配置文件中读取定义, 并动态创建Pydantic模型。
    """
    # 字典，用于存放动态创建的类
    # key是类名, value是类对象
    dynamic_models: Dict[str, Type[BaseModel]] = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    for model_name, model_config in  config.get('types', {}).items():
        fields_to_create = {}
        for field_name, field_info in model_config.get('fields', {}).items():
            # 1. 获取类型
            type_str = field_info['type']
            try:
                field_type = get_type_from_string(type_str)
            except (NameError, TypeError) as e:
                print(f"Error: Could not resolve type '{type_str}' for field '{field_name}' in model '{model_name}'. Skipping field. Details: {e}")
                continue

            # 2. 获取默认值
            # Pydantic中，必填字段的默认值是 Ellipsis (...)
            default_value = field_info.get('default', ...)
            if default_value is None: # YAML中的null会被解析为None
                default_value = ...

            # Pydantic `create_model` 需要一个 (type, default_value) 的元组
            fields_to_create[field_name] = (field_type, default_value)

        # 3. 动态创建模型
        # pydantic.create_model(模型名, 字段1=(类型, 默认值), 字段2=(类型, 默认值), ...)
        dynamic_model = create_model(
            model_name,
            **fields_to_create,
            __base__=BaseModel # 也可以从配置中动态获取基类
        )
        dynamic_models[model_name] = dynamic_model
        print(f"✅ Dynamically created model '{model_name}'")

    return dynamic_models

if __name__ == "__main__":
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 设置工作目录为脚本所在目录
    os.chdir(script_dir)

    dynamic_models = load_models_from_config('./output-format.yaml')
    if 'story' in dynamic_models:
        storyModel = dynamic_models['story']
        storyData = {
            "title": "都会早晨的困惑",
            # "artist": "匿名漫画",
            "firstScene": "在一个晴朗的早晨，两只企鹅——小墨和小白匆匆赶到了地铁站。小墨动作麻利地准备刷卡进站，而小白却站在闸机前，一脸认真地摆弄着手机。",
            "secondScene": "一分钟过去了，小墨已经站在闸机内侧，而小白还在门外低头捣鼓。小墨终于忍不住了，不耐烦地转过身，对小白喊道:\"你傻逼吗？我等你一分钟了！\"小白抬起头，一脸无奈地解释:\"我用大都会扫码呢，但这个网络有点慢。\"",
            "thirdScene": "小墨听了小白的解释，虽然心中无奈，但也只好叹了口气。终于，小白的手机屏幕亮起，发出了成功扫码的提示音。两人对视一眼，带着一丝早晨的忙乱和些许的笑意，一同踏上了前往目的地的地铁。"
        }

        mock_story = storyModel(**storyData)
        print(mock_story.model_dump_json(indent=2))