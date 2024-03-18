import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from app.models import MODELS

load_dotenv()

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
    model_raw_output: Optional[str]
    revised_article: str = Field(default=None, examples=["A very nice Item"])
    bias_topic: List = Field(default=[])
    bias_types: List = Field(default=[])


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

    output, raw_output = CLIENT.inference(article)

    if output:
        output["input"] = article
        output["model_raw_output"] = output.get('model_raw_output', raw_output)
        return output

    return response
