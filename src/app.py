from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
import json
from .backend_apis import Chatbot
from .pydantic_models import ChatRequest

app=FastAPI(debug=True)

def stream_json(message: str, thread_id: str):
    bot = Chatbot(model_name="gpt-4o", thread_id=thread_id).build_graph()
    for chunk in bot.stream(message):
        yield json.dumps({
            "thread_id": thread_id,
            "type": "message_chunk",
            "content": chunk
        }) + "\n"

@app.post("/chat")
def chat(payload: ChatRequest):
    return StreamingResponse(
        content=stream_json(payload.message, payload.thread_id),
        media_type="application/x-ndjson"
    )

@app.get("/")
def home():
    return JSONResponse(status_code=200, content={"message": "hello"})

@app.get("/chat_history")
def get_chat_history(thread_id: str = Query(...)):
    bot = Chatbot(model_name="gpt-4o", thread_id=thread_id).build_graph()
    history=bot.chat_history(thread_id=thread_id)

    return JSONResponse(status_code=200, content=history)
