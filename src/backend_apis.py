from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

CHECKPOINTER = InMemorySaver()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class Chatbot:
    def __init__(self, model_name: str, thread_id: str):
        self.model_name=model_name
        self.llm=ChatOpenAI(model=self.model_name)
        self.config = {
            'configurable': {
                'thread_id': thread_id
            }
        }
        self._compiled_graph=None
    
    def chat_node(self, state: ChatState):
        messages = state['messages']
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    # Checkpointer
    def build_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("chat_node", self.chat_node)
        graph.add_edge(START, "chat_node")
        graph.add_edge("chat_node", END)

        self._compiled_graph = graph.compile(checkpointer=CHECKPOINTER)
        return self
    
    def stream(self, user_message: str):
        if not self._compiled_graph:
            raise RuntimeError("Graph not built. Call .build_graph() first.")
        
        stream_generator=self._compiled_graph.stream(
            {"messages": [HumanMessage(user_message)]},
            config=self.config,
            stream_mode="messages"
        )

        for message_chunk, metadata in stream_generator:
            if hasattr(message_chunk, "content"):
                yield message_chunk.content