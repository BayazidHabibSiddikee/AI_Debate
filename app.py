from flask import Flask, render_template, request, jsonify, send_from_directory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
import json

app = Flask(__name__)

# Replace with any free OpenAI-compatible API
os.environ["OPENAI_API_BASE"] = "http://localhost:1234/v1"
os.environ["OPENAI_API_KEY"] = "not-needed"

llm = ChatOpenAI(model="local-model", temperature=0.7)

# Load characters from extracted JSON
CHARACTERS = []
if os.path.exists('characters.json'):
    with open('characters.json', 'r') as f:
        CHARACTERS = json.load(f)

# Serve the images from the images directory
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/api/characters', methods=['GET'])
def get_characters():
    return jsonify(CHARACTERS)

def generate_debate_turn(history, character_name, topic):
    # Find the character's system prompt
    char_info = next((c for c in CHARACTERS if c['name'] == character_name), None)
    system_prompt = char_info['system_prompt'] if char_info else "You are a debater."
    
    messages = [
        SystemMessage(content=f"{system_prompt}\nYou are participating in a group chat debate. The current topic is: {topic}. Respond naturally to the ongoing conversation. Keep your response under 3 sentences.")
    ]
    
    # Add recent history
    for msg in history[-5:]:
        if msg['speaker'] == character_name:
            messages.append(AIMessage(content=msg['text']))
        else:
            messages.append(HumanMessage(content=f"[{msg['speaker']}]: {msg['text']}"))
            
    # Prompt the LLM
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
        
    # Determine whose turn it is
    if not history:
        next_char = characters[0]
    else:
        last_speaker = history[-1]['speaker']
        last_idx = characters.index(last_speaker) if last_speaker in characters else -1
        next_char = characters[(last_idx + 1) % len(characters)]
        
    reply_text = generate_debate_turn(history, next_char, topic)
    
    return jsonify({
        "speaker": next_char,
        "text": reply_text
    })

if __name__ == '__main__':
    app.run(debug=True, port=5050)
