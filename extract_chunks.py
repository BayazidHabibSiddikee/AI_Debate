import json
import base64
import os
import re

def extract_character_data(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
        
    # Attempt to find base64 encoded chara chunk
    # Often encoded as "chara\x00eyJ..."
    match = re.search(b'chara\x00([A-Za-z0-9+/=]+)', content)
    if match:
        try:
            decoded = base64.b64decode(match.group(1)).decode('utf-8')
            return json.loads(decoded)
        except Exception:
            pass
            
    # Attempt to find raw JSON if it's not base64 encoded
    match_json = re.search(b'({"name".+?})', content)
    if match_json:
        try:
            return json.loads(match_json.group(1).decode('utf-8'))
        except Exception:
            pass
            
    return None

if __name__ == '__main__':
    cards = []
    # Retain existing characters if present
    if os.path.exists("characters.json"):
        with open("characters.json", "r") as f:
            cards = json.load(f)
            
    existing_ids = {c["id"] for c in cards}

    for file in os.listdir("images"):
        if file.endswith(".png"):
            path = f"images/{file}"
            chara_json = extract_character_data(path)
            
            if chara_json:
                name = chara_json.get('name', file.replace('.png', ''))
                char_id = name.replace(' ', '_')
                
                # Prioritize description/personality/system_prompt fields
                sys_prompt = chara_json.get('system_prompt', '')
                if not sys_prompt:
                    sys_prompt = f"{chara_json.get('description', '')} {chara_json.get('personality', '')}"
                
                if char_id not in existing_ids:
                    cards.append({
                        "id": char_id,
                        "name": name,
                        "image": path,
                        "system_prompt": sys_prompt.strip()
                    })
                    existing_ids.add(char_id)
                    print(f"Extracted {name}")

    with open("characters.json", "w") as f:
        json.dump(cards, f, indent=2)
    print(f"Total characters: {len(cards)}")
