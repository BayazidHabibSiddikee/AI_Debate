from flask import Flask, render_template, request, jsonify, send_from_directory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Config from environment
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model")

llm = ChatOpenAI(model=LLM_MODEL, temperature=0.7, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

# Ensure storage directory exists
os.makedirs("storage", exist_ok=True)
DATASET_FILE = "storage/debates_dataset.jsonl"

CHARACTERS = []
if os.path.exists('characters.json'):
    with open('characters.json', 'r') as f:
        CHARACTERS = json.load(f)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/api/characters', methods=['GET'])
def get_characters():
    return jsonify(CHARACTERS)

def get_rag_context(topic):
    # Optional: Connect to the RAG server if it's running
    try:
        res = requests.get("http://localhost:5080/api/search", params={"q": topic}, timeout=2)
        if res.status_code == 200:
            return res.json().get("context", "")
    except Exception:
        pass
    return ""

def generate_debate_turn(history, character_name, topic):
    char_info = next((c for c in CHARACTERS if c['name'] == character_name), None)
    system_prompt = char_info['system_prompt'] if char_info else "You are a debater."
    
    rag_context = get_rag_context(topic)
    context_injection = f"\nRelevant Background Knowledge:\n{rag_context}" if rag_context else ""
    
    messages = [
        SystemMessage(content=f"{system_prompt}\nYou are participating in a group chat debate. The current topic is: {topic}. {context_injection}\nRespond naturally to the ongoing conversation. Keep your response concise.")
    ]
    
    for msg in history[-5:]:
        if msg['speaker'] == character_name:
            messages.append(AIMessage(content=msg['text']))
        else:
            messages.append(HumanMessage(content=f"[{msg['speaker']}]: {msg['text']}"))
            
    response = llm.invoke(messages)
    return response.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    topic = data.get('topic', 'Dancing and Music')
    characters = data.get('characters', [])
    history = data.get('history', [])
    
    if not characters:
        return jsonify({"error": "No characters selected."}), 400
        
    if not history:
        next_char = characters[0]
    else:
        last_speaker = history[-1]['speaker']
        last_idx = characters.index(last_speaker) if last_speaker in characters else -1
        next_char = characters[(last_idx + 1) % len(characters)]
        
    reply_text = generate_debate_turn(history, next_char, topic)
    
    # Export to Dataset for training
    with open(DATASET_FILE, "a", encoding="utf-8") as f:
        turn_data = {
            "topic": topic,
            "speaker": next_char,
            "text": reply_text
        }
        f.write(json.dumps(turn_data) + "\n")
    
    return jsonify({
        "speaker": next_char,
        "text": reply_text
    })

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, port=5050)
