import os

from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.hf_llama2 import inference, init_client
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add(f"logs/{__name__}.log", rotation="500 MB")

CLIENT = init_client(model_name=os.getenv("MODEL_NAME"), token=os.getenv("MODEL_TOKEN"))
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


class Body(BaseModel):
    article: str


@app.post(
    "/debias",
    response_model=DebiasResponse
)
def debias(body: Body):
    article = body.article
    words = article.split()
    if len(words) <= 1:
        return dict(input=body.article, biased="no", bias_topic=[], bias_types=[], revised_article=None)
    output = inference(body.article, client=CLIENT, max_new_tokens=MAX_NEW_TOKENS)

    if not output:
        return dict(input=body.article, biased="no", bias_topic=[], bias_types=[], revised_article=None)

    if output["biased"] == "no":
        return dict(input=body.article, biased=output["biased"], bias_topic=[], bias_types=[], revised_article=None)
    return output
