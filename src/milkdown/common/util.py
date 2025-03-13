import ast
from datetime import datetime
import json
import os
import re

import yaml
from fastapi import HTTPException
from milkdown.common.logging import logger


def generate_filepath(filename: str, filepath: str) -> str:
    os.makedirs(filepath, exist_ok=True)
    return os.path.join(filepath, filename)


def get_file_name(path: str) -> str:
    try:
        file = os.path.basename(path)
        file_name = ".".join(file.split(".")[:-1])
        return file_name
    except Exception as err:
        logger.error(f"An error was found when capturing the file name: {err}")
        return ""


def get_local_time(
    only_day: bool = False,
    only_time: bool = False,
    in_chinese: bool = False
) -> str:
    
    time_format = "%Y年%-m月%-d日 %-H点%M分%S秒" if in_chinese else "%Y-%-m-%-d %H:%M:%S"
    if only_day:
        time_format = "%Y年%-m月%-d日" if in_chinese else "%Y-%-m-%-d"
    if only_time:
        time_format = "%-H点%M分" if in_chinese else "%-H:%M"

    return datetime.now().strftime(time_format)


def camel_to_snake(name: str) -> str:
    """将驼峰命名（CamelCase）转换为蛇形命名（snake_case）

    Args:
        name (str): 驼峰格式的字符串名

    Returns:
        str: 蛇形字符串名
    """
    return re.sub(r'(?<!^)([A-Z])', r'_\1', name).lower()


def text_2_json(text: str) -> dict | list | None:
    text = text.replace("```json\n", "").replace("\n```", "").replace("\n", "")
    try:
        result = ast.literal_eval(text)
        return result
    except Exception as err:
        return None


def load_yaml(yaml_path: str) -> dict:
    try:
        with open(yaml_path) as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as err:
        raise Exception(f"[YAML Reader] Error occured when read YAML from path '{yaml_path}'. Error: {err}") from err


def load_yamls_under_folder(folder: str) -> dict[str, dict]:
    if os.path.isdir(folder):
        # collect all yaml file
        files = [
            os.path.join(folder, file) 
            for file in os.listdir(folder) 
            if os.path.isfile(os.path.join(folder, file)) 
            and (file.endswith(".yaml") or file.endswith(".yml"))
        ]
        result = {
            get_file_name(file): load_yaml(file)
            for file in files
        }
        return result
    return {}


def load_json(json_path: str) -> dict | list:
    try:
        with open(json_path) as json_file:
            return json.load(json_file)
    except Exception as err:
        raise Exception(f"[JSON Reader] Error occurred when read JSON from path '{json_file}'. Error: {err}") from err


def save_json(file_path: str, data: dict) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
