import os
from dotenv import load_dotenv
import json
from loguru import logger

logger.add(f"logs/{__name__}.log", rotation="500 MB")

load_dotenv()

with open(os.getenv('PROMPT_FILE'), 'r') as f:
    TASK = f.read()

def handle_error(text, decoder=json.JSONDecoder()):
    fixed_data = {}
    bias_types = []
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            sub_text = text[match:]
            if "input" in sub_text:
                start_index = sub_text.find('"input":')
                end_index = sub_text.find('"revised_article":')
                input_text = sub_text[start_index + len('"input": '):end_index]
                fixed_data["input"] = input_text
            if "revised_article" in sub_text:
                start_index = sub_text.find('"revised_article":')
                end_index = sub_text.find('"bias_types":')
                input_text = sub_text[start_index + len('"revised_article": '):end_index]
                fixed_data["revised_article"] = input_text
            result, index = decoder.raw_decode(text[match:])
            bias_types.append(result)
            pos = match + index
        except ValueError:
            pos = match + 1
    fixed_data["bias_types"] = bias_types
    return fixed_data


def parse_output(input_text):
    logger.info(f"parsing {input_text}")
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
