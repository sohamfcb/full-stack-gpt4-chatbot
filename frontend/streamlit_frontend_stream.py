import streamlit as st
# from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import requests
from utils import stream_text

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

URL="http:127.0.0.1/8000/chat"

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

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

        for chunk in stream_text(message=user_input, thread_id="1"):
            full_text+=chunk
            placeholder.markdown(full_text)

    st.session_state['message_history'].append({'role': 'assistant', 'content': full_text})