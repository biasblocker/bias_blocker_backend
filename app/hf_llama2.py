from huggingface_hub import InferenceClient, utils, inference
import huggingface_hub
from app.debias.utils import parse_output
from loguru import logger

PROMPT = """<s>[INST] <<SYS>>
{sys_message}
<</SYS>>
{sentence} [/INST]
"""

with open('prompts/debias_with_examples.txt', 'r') as f:
    sys_message = f.read()


def init_client(model_name, token):
    return InferenceClient(model=model_name, token=token)


def format_query(query):
    return PROMPT.format(sentence=query, sys_message=sys_message)


def construct_err_msg(client, e, err_count, query):
    logger.info(f"{e}\nRetrying the request.")
    if err_count <= 100:
        inference(query, client, err_count)
    else:
        logger.error(f"Can not process {query} due to {e}")


def inference(query, client, err_count=0, max_new_tokens=250):
    try:
        output = parse_output(
            client.text_generation(format_query(query),
                                   max_new_tokens=max_new_tokens))
        return output
    except utils._errors.HfHubHTTPError as e:
        err_count += 1
        construct_err_msg(client, e, err_count, query)
    except huggingface_hub.inference._text_generation.OverloadedError as e:
        err_count += 1
        construct_err_msg(client, e, err_count, query)
