import json

from dotenv import load_dotenv
from loguru import logger

logger.add(f"logs/{__name__}.log", rotation="500 MB")

load_dotenv()


def handle_error(text):
    fixed_data = {}
    bias_types = []
    pos = 0

    while True:
        match = text.find('{', pos)
        if match == -1:
            break

        try:
            sub_text = text[match:]

            input_start = sub_text.find('"input":')
            revised_start = sub_text.find('"revised_article":')

            if input_start != -1:
                input_text = sub_text[input_start + len('"input": '):revised_start].strip('", ')
                fixed_data["input"] = input_text

            if revised_start != -1:
                revised_text = sub_text[revised_start + len('"revised_article": '):].strip('", ')
                fixed_data["revised_article"] = revised_text

            result = json.loads(sub_text)
            bias_types.append(result)
            pos = match + sub_text.rindex('}') + 1

        except json.JSONDecodeError:
            pos = match + 1

    fixed_data["bias_types"] = bias_types
    return fixed_data


def parse_output(input_text):
    start_index = input_text.find('{')
    end_index = input_text.rfind('}') + 1
    json_string = input_text[start_index:end_index]

    try:
        data = json.loads(json_string)
        return data
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        logger.info("Fixing it...")
        fixed_data = handle_error(json_string)
        return fixed_data


def read_task_prompt(fname):
    with open(fname, 'r') as f:
        return f.read()
