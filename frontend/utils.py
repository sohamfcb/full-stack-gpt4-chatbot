import requests
import json
import uuid

def stream_text(thread_id: str, message: str):
    with requests.post(
        "http://127.0.0.1:8000/chat",
        json={"thread_id": thread_id, "message": message},
        stream=True
    ) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                yield data["content"]

def generate_thread_id():
    return uuid.uuid4()