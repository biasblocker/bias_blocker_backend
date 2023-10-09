from huggingface_hub import InferenceClient, utils, inference
from app.debias.utils import parse_output
from loguru import logger

SYS_MESSAGE = open('prompts/debias.txt', 'r')
PROMPT = """<s>[INST] <<SYS>>
{sys_message}
<</SYS>>
{sentence} [/INST]
"""

with open('prompts/debias.txt', 'r') as f:
    sys_message = f.read()


def init_client(model_name, token):
    return InferenceClient(model=model_name, token=token)


def format_query(query):
    return PROMPT.format(sentence=query, sys_message=SYS_MESSAGE)


def inference(query, client, err_count=0, max_new_tokens=250):
    try:
        output = parse_output(
            client.text_generation(PROMPT.format(sentence=query, sys_message=sys_message), max_new_tokens=max_new_tokens))
        return output
    except utils._errors.HfHubHTTPError or inference._text_generation.OverloadedErrors as e:
        err_count += 1
        logger.info(f"{e}\nRetrying the request.")
        if err_count <=10:
            inference(query, client, err_count)
