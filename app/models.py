from app.hf_llama2 import Llama2API
from app.chat_gpt import ChatGPTAPI

MODELS = {
    "llama": Llama2API,
    "chatgpt": ChatGPTAPI
}
