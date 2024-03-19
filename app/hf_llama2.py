import os
from huggingface_hub import InferenceClient, utils
import huggingface_hub
from app.utils import parse_output, read_task_prompt
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

PROMPT = """<s>[INST] <<SYS>>
{sys_message}
<</SYS>>
{sentence} [/INST]
"""

TASK = read_task_prompt(os.getenv("PROMPT_FILE"))

class Llama2API:
    def __init__(self):
        self.client = InferenceClient(model=os.getenv('MODEL_NAME'), token=os.getenv('MODEL_TOKEN'))
        self.max_new_tokens = os.getenv('MAX_NEW_TOKENS')

    def _format_query(self, query):
        return PROMPT.format(sentence=query, sys_message=TASK)

    def inference(self, query, err_count=0):
        logger.info(f"querying {query}")
        try:
            output = self.client.text_generation(PROMPT.format(sentence=query, sys_message=TASK),
                                                 max_new_tokens=self.max_new_tokens)
            logger.info(f"chatgpt returned a result")
            parsed_doc = parse_output(output)
            logger.info(f"parsing the document")
            return parsed_doc, output
        except utils._errors.HfHubHTTPError as e:
            err_count += 1
            logger.info(f"{e}\nRetrying the request.")
            if err_count <= 100:
                self.inference(query, err_count)
        except huggingface_hub.inference._text_generation.OverloadedError as e:
            err_count += 1
            logger.info(f"{e}\nRetrying the request.")
            if err_count <= 100:
                self.inference(query, err_count)
