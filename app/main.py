import os
from diskcache import Cache
from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI, HTTPException, Request, status, Form
from fastapi.middleware.cors import CORSMiddleware
# from app.hf_llama2 import inference, init_client
from app.models import MODELS
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

cache = Cache("tmp")

logger.add(f"logs/{__name__}.log", rotation="500 MB")

# CLIENT = init_client(model_name=os.getenv("MODEL_NAME"), token=os.getenv("MODEL_TOKEN"))
CLIENT = MODELS[os.getenv("ACTIVE")]()

MAX_NEW_TOKENS = os.getenv("MAX_NEW_TOKENS")

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebiasResponse(BaseModel):
    input: str = Field(examples=["Foo"])
    biased: str = Field(default="no")
    revised_article: str = Field(default=None, examples=["A very nice Item"])
    bias_topic: List = Field(default=[])
    bias_types: List = Field(default=[])

@cache.memoize()
@app.post(
    "/debias",
    response_model=DebiasResponse
)
def debias(article: str=Form(...)):
    words = article.split()
    if len(words) <= 1:
        return dict(input=article, biased="no", bias_topic=[], bias_types=[], revised_article=None)
    output = CLIENT.inference(article)
    if not output:
        return dict(input=article, biased="no", bias_topic=[], bias_types=[], revised_article=None)

    if "biased" in output and output["biased"] == "no":
        return dict(input=article, biased=output["biased"], bias_topic=[], bias_types=[], revised_article=None)
    elif "biased" not in output:
        return dict(input=article, biased="no", bias_topic=[], bias_types=[], revised_article=None)

    return output
