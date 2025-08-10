from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

CHECKPOINTER = InMemorySaver()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class Chatbot:
    def __init__(self, model_name: str):
        self.model_name=model_name
        self.llm=ChatOpenAI(model=self.model_name)
        self.config = None
        self._compiled_graph=None
        self.checkpointer=None
    
    def chat_node(self, state: ChatState):
        messages = state['messages']
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    # Checkpointer
    def build_graph(self, _sqlite=False):
        graph = StateGraph(ChatState)
        graph.add_node("chat_node", self.chat_node)
        graph.add_edge(START, "chat_node")
        graph.add_edge("chat_node", END)

        if _sqlite:
            conn=sqlite3.connect(database="db/chatbot.db", check_same_thread=False)
            # sqlite_checkpointer=SqliteSaver(conn=conn)
            self.checkpointer=SqliteSaver(conn=conn)
            self._compiled_graph=graph.compile(checkpointer=self.checkpointer)
            self.is_persistent_storage=True
            return self

        self.checkpointer=InMemorySaver()
        self._compiled_graph = graph.compile(checkpointer=self.checkpointer)
        return self
    
    def stream(self, user_message: str, thread_id: str):
        if not self._compiled_graph:
            raise RuntimeError("Graph not built. Call .build_graph() first.")

        self.config={
            "configurable": {
                "thread_id": thread_id
            }
        }
        stream_generator=self._compiled_graph.stream(
            {"messages": [HumanMessage(user_message)]},
            config=self.config,
            stream_mode="messages"
        )

        for message_chunk, metadata in stream_generator:
            if hasattr(message_chunk, "content"):
                yield message_chunk.content

    def chat_history(self, thread_id: str):

        self.config={
            "configurable": {
                "thread_id": thread_id
            }
        }
        history=self._compiled_graph.get_state(config=self.config).values
        messages = history.get("messages", [])

        # Convert each BaseMessage into a dict
        serialized_messages = []
        for msg in messages:
            serialized_messages.append({
                "type": msg.type,    # "human", "ai", "system"
                "content": msg.content
            })

        return {"messages": serialized_messages}
    
    def get_chat_threads(self):
        if not self.is_persistent_storage:
            raise RuntimeError("Object of class Chatbot not built with _sqlite = True.")
        
        all_threads=set()

        for checkpoint in self.checkpointer.list(None):
            all_threads.add(checkpoint.config["configurable"]["thread_id"])

        return list(all_threads)
        