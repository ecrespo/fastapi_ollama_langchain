import asyncio
import os
from typing import AsyncIterable
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
from pydantic import BaseModel

# Import and instanceaded logguru
from loguru import logger
logger.add("file_{time}.log")


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

@app.post("/stream_chat")
async def stream_chat(message: Message):
    generator = send_message(message.content)
    return StreamingResponse(generator, media_type="text/event-stream")


