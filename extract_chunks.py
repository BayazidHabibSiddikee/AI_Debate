import struct
import json
import base64
import os

def extract_png_text(filepath):
    with open(filepath, 'rb') as f:
        # Check signature
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            return None
        
        while True:
            length_bytes = f.read(4)
            if len(length_bytes) != 4:
                break
            length = struct.unpack('>I', length_bytes)[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            crc = f.read(4)
            
            if chunk_type in (b'tEXt', b'iTXt'):
                try:
                    # tEXt format: keyword + null + text
                    if chunk_type == b'tEXt':
                        parts = chunk_data.split(b'\x00', 1)
                        if len(parts) == 2:
                            keyword, text = parts
                            return (keyword.decode('latin-1'), text.decode('latin-1'))
                except Exception:
                    pass
    return None

if __name__ == '__main__':
    cards = []
    for file in os.listdir("images"):
        if file.endswith(".png"):
            path = f"images/{file}"
            res = extract_png_text(path)
            if res:
                keyword, data = res
                if keyword == 'chara':
                    try:
                        decoded = base64.b64decode(data).decode('utf-8')
                        chara_json = json.loads(decoded)
                        name = chara_json.get('name', file)
                        sys_prompt = chara_json.get('system_prompt', chara_json.get('description', ''))
                        
                        cards.append({
                            "id": name.replace(' ', '_'),
                            "name": name,
                            "image": path,
                            "system_prompt": sys_prompt
                        })
                        print(f"Extracted {name}")
                    except Exception as e:
                        print(f"Error parsing chara in {file}: {e}")

    # Add Marin manually
    cards.append({
        "id": "Marin",
        "name": "Marin",
        "image": "images/default_marin.png",
        "system_prompt": "You are Marin, an AI designed with dry humor and technical prowess."
    })
    
    with open("characters.json", "w") as f:
        json.dump(cards, f, indent=2)
    print(f"Total characters: {len(cards)}")
