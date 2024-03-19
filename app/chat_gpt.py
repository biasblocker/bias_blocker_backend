import os
from app.utils import parse_output
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger
from app.utils import read_task_prompt

load_dotenv()

TASK = read_task_prompt(os.getenv("PROMPT_FILE"))

class ChatGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.temperature = os.environ["OPENAI_TEMPERATURE"]

    def inference(self, query):
        logger.info(f"Prompting {query}")
        completion = self.client.chat.completions.create(
            model=os.getenv("CHATGPT_MODEL"),
            messages=[
                {"role": "system", "content": TASK},
                {"role": "user", "content": query}
            ],
            temperature=float(self.temperature)
        )
        logger.info(f"chatgpt returned a result")
        raw_output = completion.choices[0].message.content
        logger.info(f"the document is parsing")
        parsed_output = parse_output(raw_output)
        logger.info(f"the document parsed")
        return parsed_output, raw_output
