from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
import json
import logging
import uuid
from datetime import datetime
import requests

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configuration from environment
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
RAG_SERVER_URL = os.getenv("RAG_SERVER_URL", "http://localhost:5080")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

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
CONVERSATION_ID = str(uuid.uuid4())  # Unique ID for each session

# Load characters with error handling
CHARACTERS = []
CHARACTERS_FILE = 'characters.json'

try:
    if os.path.exists(CHARACTERS_FILE):
        with open(CHARACTERS_FILE, 'r') as f:
            CHARACTERS = json.load(f)
        logger.info(f"Loaded {len(CHARACTERS)} characters from {CHARACTERS_FILE}")
    else:
        logger.warning(f"{CHARACTERS_FILE} not found. Run: python extract_chunks.py")
        # Create empty file
        with open(CHARACTERS_FILE, 'w') as f:
            json.dump([], f)
except Exception as e:
    logger.error(f"Failed to load characters: {e}")

# Serve images with fallback
@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        if os.path.exists(os.path.join('images', filename)):
            return send_from_directory('images', filename)
        raise FileNotFoundError
    except FileNotFoundError:
        logger.warning(f"Image not found: {filename}")
        # Return placeholder SVG
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" fill="#1f2937" rx="50"/>
            <text x="50" y="55" text-anchor="middle" fill="white" font-size="20">?</text>
        </svg>'''
        return Response(svg, mimetype='image/svg+xml')

@app.route('/api/characters', methods=['GET'])
def get_characters():
    return jsonify(CHARACTERS)

def get_rag_context(topic):
    """Fetch context from RAG server if available."""
    try:
        response = requests.post(
            f"{RAG_SERVER_URL}/search",
            json={"query": topic, "k": 5},
            timeout=2
        )
        if response.status_code == 200:
            results = response.json().get("results", [])
            context = "\n".join([r.get("content", "")[:500] for r in results[:3]])
            return f"\n\nRelevant Background Knowledge:\n{context}"
    except Exception as e:
        logger.debug(f"RAG server unavailable: {e}")
    return ""

def generate_debate_turn(history, character_name, topic):
    # Find the character's system prompt
    char_info = next((c for c in CHARACTERS if c['name'] == character_name), None)
    if char_info:
        system_prompt = char_info.get('system_prompt', f"You are {character_name}.")
    else:
        system_prompt = f"You are {character_name}, a debater."
        logger.warning(f"Character '{character_name}' not found in {CHARACTERS_FILE}")

    # Get RAG context
    rag_context = get_rag_context(topic)

    messages = [
        SystemMessage(content=f"""{system_prompt}

You are participating in a group chat debate.
Current topic: {topic}
{rag_context}

Respond naturally to the ongoing conversation.
Keep your response concise (1-3 sentences).""")
    ]

    # Add recent history (last 5 turns)
    for msg in history[-5:]:
        if msg['speaker'] == character_name:
            messages.append(AIMessage(content=msg['text']))
        else:
            messages.append(HumanMessage(content=f"[{msg['speaker']}]: {msg['text']}"))

    # Prompt the LLM
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        return f"[Error: Could not generate response - {str(e)}]"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    topic = data.get('topic', 'General Discussion')
    characters = data.get('characters', [])
    history = data.get('history', [])

    if not characters:
        return jsonify({"error": "No characters selected. Choose at least 2."}), 400

    # Determine whose turn it is (round-robin)
    if not history:
        next_char = characters[0]
    else:
        last_speaker = history[-1]['speaker']
        last_idx = characters.index(last_speaker) if last_speaker in characters else -1
        next_char = characters[(last_idx + 1) % len(characters)]

    # Find character info for export
    char_info = next((c for c in CHARACTERS if c['name'] == next_char), None) or {}

    reply_text = generate_debate_turn(history, next_char, topic)

    # Export to dataset
    try:
        turn_data = {
            "conversation_id": CONVERSATION_ID,
            "topic": topic,
            "speaker": next_char,
            "text": reply_text,
            "timestamp": datetime.now().isoformat(),
            "character": char_info
        }
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn_data) + "\n")
    except Exception as e:
        logger.error(f"Failed to export turn: {e}")

    return jsonify({
        "speaker": next_char,
        "text": reply_text,
        "conversation_id": CONVERSATION_ID
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "operational",
        "characters_loaded": len(CHARACTERS),
        "dataset_path": DATASET_FILE,
        "dataset_exists": os.path.exists(DATASET_FILE)
    })

if __name__ == '__main__':
    logger.info(f"Starting Debate Simulator on port 5050")
    logger.info(f"LLM: {LLM_MODEL} at {OPENAI_API_BASE}")
    logger.info(f"RAG Server: {RAG_SERVER_URL}")
    app.run(debug=FLASK_DEBUG, port=5050)
