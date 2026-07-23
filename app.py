from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os

app = Flask(__name__)

# Replace with any free OpenAI-compatible API (e.g. Groq, Together, or Local LM Studio)
os.environ["OPENAI_API_BASE"] = "http://localhost:1234/v1" # Example local free endpoint
os.environ["OPENAI_API_KEY"] = "not-needed" # Or put free API key here

llm = ChatOpenAI(model="local-model", temperature=0.7)

# Pre-defined character personas
PERSONAS = {
    "Marin": "You are Marin, a sharp, tech-savvy AI character with dry humor.",
    "Bayazid": "You are Bayazid, a logical and ambitious engineer.",
    "Genny": "You are Genny, an overly enthusiastic and creative artist.",
    "Zane": "You are Zane, a laid-back gamer who loves discussing strategies."
}

def generate_debate_turn(history, character_name, topic):
    messages = [
        SystemMessage(content=f"{PERSONAS[character_name]}\nYou are participating in a group chat. The current topic is: {topic}. Respond naturally to the ongoing conversation. Keep your response under 3 sentences.")
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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    topic = data.get('topic', 'Dancing and Music')
    characters = data.get('characters', ['Marin', 'Bayazid'])
    history = data.get('history', [])
    
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
