import json
import asyncio
from slowapi import Limiter
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from chatbot.bot import ChatBot
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from chatbot.genai_handler import GenAIHandler
from fastapi.responses import JSONResponse, StreamingResponse


load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Smart ChatBot API")
app.state.limiter = limiter

templates = Jinja2Templates(directory="templates")

chatbot = ChatBot()
genai = GenAIHandler()

class Message(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.options("/chat/stream")
async def chat_stream_options():
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.post("/chat/stream")
async def chat_stream(message: Message):
    try:
        intent_response = chatbot.get_response(message.prompt)
        if intent_response["confidence"] >= 0.8:
            async def intent_stream():
                words = intent_response["response"].split()
                for word in words:
                    yield word + " "
                    await asyncio.sleep(0.1)
            
            return StreamingResponse(
                intent_stream(),
                media_type='text/event-stream',
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        else:
            return StreamingResponse(
                genai.generate_response_stream(message.prompt, message.session_id),
                media_type='text/event-stream',
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": f"Internal server error: {str(e)}",
                "source": "server"
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

@app.get("/health")
async def health_check():
    health_status = {
        "server": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        },
        "openai": await check_openai_health()
    }
    
    if not health_status["openai"]["status"] == "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status

async def check_openai_health():
    try:
        response = await genai.generate_response_stream("test").__anext__()
        return {
            "status": "healthy",
            "message": "OpenAI services are accessible"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id= "default"):
    genai.clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}
