import os

from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.hf_llama2 import inference, init_client, format_query
from loguru import logger

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
    revised_article: str | None = Field(default=None, examples=["A very nice Item"])
    bias_types: List | None


class HTTPErrorResponse(BaseModel):
    input: str
    revised_article: str
    bias_types: List


class Body(BaseModel):
    article: str


@app.post(
    "/debias",
    response_model=DebiasResponse
)
def debias(body: Body):
    output = inference(format_query(body.article), client=CLIENT, max_new_tokens=MAX_NEW_TOKENS)
    return output
