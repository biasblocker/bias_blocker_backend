import os
from app.utils import parse_output, TASK
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatGPTAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.temperature = os.environ["OPENAI_TEMPERATURE"]

    def inference(self, query):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": TASK},
                {"role": "user", "content": query}
            ],
            temperature=float(self.temperature)
        )
        return parse_output(completion.choices[0].message.content)
