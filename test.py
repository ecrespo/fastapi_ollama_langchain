from dotenv import load_dotenv
# import ollama chat
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
load_dotenv()

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

chat = ChatOllama(
    base_url="http://localhost:11434",
    model="llama2:7b",
    callbacks=[StreamingStdOutCallbackHandler()],
    streaming=True,
    temperature=0,
    verbose=True
)
print("\n")
print(chat)

message = HumanMessage(content="Write me a song about sparkling water.")
print(message)
print(chat.invoke([message]))

