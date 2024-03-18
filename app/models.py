from app.chain_prompting import ChatGPTChain
from app.chat_gpt import ChatGPTAPI
from app.hf_llama2 import Llama2API

MODELS = {
    "llama": Llama2API,
    "chatgpt": ChatGPTAPI,
    "chatgpt-chain": ChatGPTChain
}
