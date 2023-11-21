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
    model_raw_output: str
    revised_article: str = Field(default=None, examples=["A very nice Item"])
    bias_topic: List = Field(default=[])
    bias_types: List = Field(default=[])


@cache.memoize()
@app.post(
    "/debias",
    response_model=DebiasResponse
)
def debias(article: str = Form(...)):
    response = {
        "input": article,
        "biased": "undecided",
        "bias_types": [],
        "bias_topic": [],
        "revised_article": None,
        "model_raw_output": None,
    }

    words = article.split()

    if len(words) <= 1:
        pass

    output, raw_output = CLIENT.inference(article)

    logger.info(f"Output: {output}")

    if not output or "biased" not in output:
        response["biased"] = "no"
    elif output["biased"] == "yes":
        response["biased"] = output.get('biased', response['biased'])
        response["revised_article"] = output.get('revised_article', response['revised_article'])
        response["bias_types"] = output.get('bias_types', response['bias_types'])
        if not response["bias_types"]:
            response["bias_types"] = []

        response["bias_topic"] = output.get('bias_topic', response['bias_topic'])
        if not response["bias_topic"]:
            response["bias_topic"] = []

    response["model_raw_output"] = output.get('model_raw_output', raw_output)

    return response
