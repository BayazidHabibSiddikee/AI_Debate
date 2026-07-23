from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
import json
import logging
import uuid
from datetime import datetime
import httpx
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

app = FastAPI(title="AI Debate Simulator")

# Configuration from environment
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
RAG_SERVER_URL = os.getenv("RAG_SERVER_URL", "http://localhost:5080")
DEBUG_MODE = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

# Initialize LLM with error handling
try:
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.7,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    logger.info(f"LLM initialized: {LLM_MODEL} at {OPENAI_API_BASE}")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    raise RuntimeError(f"Cannot start without LLM: {e}")

# Ensure directories exist
os.makedirs("storage", exist_ok=True)
os.makedirs("images", exist_ok=True)

# Dataset file
DATASET_FILE = "storage/debates_dataset.jsonl"
CONVERSATION_ID = str(uuid.uuid4())

# Load characters
CHARACTERS = []
CHARACTERS_FILE = 'characters.json'

def load_characters():
    global CHARACTERS
    try:
        if os.path.exists(CHARACTERS_FILE):
            with open(CHARACTERS_FILE, 'r') as f:
                CHARACTERS = json.load(f)
            logger.info(f"Loaded {len(CHARACTERS)} characters")
        else:
            with open(CHARACTERS_FILE, 'w') as f:
                json.dump([], f)
    except Exception as e:
        logger.error(f"Failed to load characters: {e}")

load_characters()

# Mount templates and static files
templates = Jinja2Templates(directory="templates")

# Serve images with fallback
@app.get("/images/{filename}")
async def serve_image(filename: str):
    file_path = os.path.join("images", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Return placeholder SVG if missing
    logger.warning(f"Image not found: {filename}")
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <rect width="100" height="100" fill="#1f2937" rx="50"/>
        <text x="50" y="55" text-anchor="middle" fill="white" font-size="20">?</text>
    </svg>'''
    return Response(content=svg, media_type='image/svg+xml')

@app.get("/api/characters")
async def get_characters():
    return JSONResponse(content=CHARACTERS)

async def get_rag_context(topic: str) -> str:
    """Fetch context from RAG server asynchronously."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                f"{RAG_SERVER_URL}/context",
                json={"query": topic, "k": 5}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                context = "\n".join([r.get("content", "")[:500] for r in results[:3]])
                return f"\n\nRelevant Background Knowledge:\n{context}"
    except Exception as e:
        logger.debug(f"RAG server unavailable: {e}")
    return ""

class ChatRequest(BaseModel):
    topic: str = "General Discussion"
    characters: List[str] = []
    history: List[Dict[str, Any]] = []

@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.characters:
        raise HTTPException(status_code=400, detail="No characters selected. Choose at least 2.")

    # Determine whose turn it is
    if not req.history:
        next_char = req.characters[0]
    else:
        last_speaker = req.history[-1].get('speaker', '')
        try:
            last_idx = req.characters.index(last_speaker)
        except ValueError:
            last_idx = -1
        next_char = req.characters[(last_idx + 1) % len(req.characters)]

    char_info = next((c for c in CHARACTERS if c['name'] == next_char), None) or {}
    system_prompt = char_info.get('system_prompt', f"You are {next_char}, a debater.")
    
    rag_context = await get_rag_context(req.topic)

    messages = [
        SystemMessage(content=f"{system_prompt}\n\nYou are participating in a group chat debate.\nCurrent topic: {req.topic}\n{rag_context}\n\nRespond naturally to the ongoing conversation.\nKeep your response concise (1-3 sentences).")
    ]

    for msg in req.history[-5:]:
        speaker = msg.get('speaker', 'Unknown')
        text = msg.get('text', '')
        if speaker == next_char:
            messages.append(AIMessage(content=text))
        else:
            messages.append(HumanMessage(content=f"[{speaker}]: {text}"))

    try:
        # Use sync invoke inside an executor to not block if it's heavy, or just await it if using async llm client.
        response = await llm.ainvoke(messages)
        reply_text = response.content
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        reply_text = f"[Error: Could not generate response - {str(e)}]"

    # Export to dataset
    try:
        turn_data = {
            "conversation_id": CONVERSATION_ID,
            "topic": req.topic,
            "speaker": next_char,
            "text": reply_text,
            "timestamp": datetime.now().isoformat(),
            "character": char_info
        }
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn_data) + "\n")
    except Exception as e:
        logger.error(f"Failed to export turn: {e}")

    return {
        "speaker": next_char,
        "text": reply_text,
        "conversation_id": CONVERSATION_ID
    }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "characters_loaded": len(CHARACTERS),
        "dataset_path": DATASET_FILE,
        "dataset_exists": os.path.exists(DATASET_FILE)
    }

if __name__ == '__main__':
    import uvicorn
    logger.info(f"Starting FastAPI Debate Simulator on port 5050")
    logger.info(f"LLM: {LLM_MODEL} at {OPENAI_API_BASE}")
    uvicorn.run("app:app", host="0.0.0.0", port=5050, reload=DEBUG_MODE)
