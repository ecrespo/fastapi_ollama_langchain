import asyncio
import os
import ollama
from typing import AsyncIterable
from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
from pydantic import BaseModel

# Import and instanceaded logguru
from loguru import logger
#logger.add("./logs/file_{time}.log")


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str

async def send_message(content: str) -> AsyncIterable[str]:

    callback = AsyncIteratorCallbackHandler()
    model = ChatOllama(
        base_url="http://localhost:11434",
        model="llama2:7b",
        callbacks=[callback],
        streaming=True,
        temperature=0,
        verbose=True
    )



    task = asyncio.create_task(
        model.agenerate(
            [[HumanMessage(content=content)]]  # type: ignore
        )
    )
    try:
        # await callback.on_chat_model_start({"model": "llama2:7b", "base_url": "http://localhost:11434"})
        async for token in callback.aiter():
            yield token
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        callback.done.set()

    await task

@app.post("/stream_chat",status_code=status.HTTP_200_OK)
async def stream_chat(message: Message):
    generator = send_message(message.content)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.get("/models/",status_code=status.HTTP_200_OK)
async def list_models()-> list[str]:
    result = ollama.list()["models"]
    resp = [item["model"] for item in result]
    logger.info(f"List of models: {resp}")

    return resp

@app.get("/models/{model_name}",status_code=status.HTTP_200_OK)
async def get_model(model_name: str):
    try:
        result = ollama.show(model_name)
        logger.info(f"Model details: {result}")
        return result
    except ollama._types.ResponseError:
        raise HTTPException(status_code=status.HTTP_200_OK , detail="Model not found")