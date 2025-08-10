import streamlit as st
from langchain_core.messages import HumanMessage
import requests
from utils import stream_text, generate_thread_id, fetch_all_threads

from dotenv import load_dotenv
import os

load_dotenv()
chat_history_url=os.getenv("CHAT_HISTORY_URL")


def load_converstation(thread_id):
    response=requests.get(chat_history_url, params={"thread_id": thread_id})
    return response.json()

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
        

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"]=fetch_all_threads()

add_thread(st.session_state["thread_id"])

# with st.sidebar:
st.sidebar.title("CloseAI 2.0")
new_chat_button=st.sidebar.button("New Chat")
st.sidebar.header("My Chats")

for thread_id in st.session_state["chat_threads"]:
    if st.sidebar.button(str(thread_id)):
        conv_hist=load_converstation(thread_id=thread_id)["messages"]

        for conv in conv_hist:
            with st.chat_message(conv["type"]):
                st.markdown(conv["content"])

if new_chat_button:
    reset_chat()
    st.text(st.session_state["thread_id"])

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message("assistant"):
        placeholder=st.empty()
        full_text=""

        for chunk in stream_text(message=user_input, thread_id=str(st.session_state.thread_id)):
            full_text+=chunk
            placeholder.markdown(full_text)

    st.session_state['message_history'].append({'role': 'assistant', 'content': full_text})