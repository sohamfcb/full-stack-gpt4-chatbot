import streamlit as st
import requests
import json

st.title("Streaming Chatbot")

thread_id = st.text_input("Thread ID", value="1")
message = st.text_input("Message", value="Hello AI!")

if st.button("Send"):
    with st.spinner("Streaming..."):
        # Placeholder for live text
        placeholder = st.empty()
        full_text = ""

        with requests.post(
            "http://127.0.0.1:8000/chat",
            json={"thread_id": thread_id, "message": message},
            stream=True
        ) as r:
            for line in r.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data["content"]
                    full_text += chunk
                    placeholder.write(full_text)
