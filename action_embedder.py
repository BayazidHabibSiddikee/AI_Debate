import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer
import json

class ActionMapper(nn.Module):
    def __init__(self, embedding_dim, num_actions):
        super(ActionMapper, self).__init__()
        self.fc1 = nn.Linear(embedding_dim, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, num_actions)
        
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def train_action_model(texts, actions_one_hot, num_actions, epochs=1000):
    # 1. Load Embedding Model
    print("Loading Sentence Transformer...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Encoding texts...")
    embeddings = embedder.encode(texts, convert_to_tensor=True)
    targets = torch.tensor(actions_one_hot, dtype=torch.float32)
    
    # 2. Setup Neural Network for Regression/Classification Loop
    model = ActionMapper(embedding_dim=embeddings.shape[1], num_actions=num_actions)
    criterion = nn.MSELoss() # Or BCEWithLogitsLoss for Multi-label classification
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 3. The Regression Loop
    print("Starting training loop...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(embeddings)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 100 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
            
    print("Training complete. Saving model...")
    torch.save(model.state_dict(), "action_mapper_weights.pth")
    return model, embedder

# Example Usage
if __name__ == "__main__":
    # Mock data: Text -> One-hot encoded actions (118 animations total)
    # E.g., [dance, exhaust, drama_interaction, joy, ...]
    sample_texts = [
        "Let's show them some moves!",
        "I am so tired, I need to sleep.",
        "How dare you betray me like this!",
        "I am so happy to see you!"
    ]
    
    num_total_actions = 118 # 118 BVH files
    # One-hot encoding examples (Mocked)
    sample_targets = [
        [1.0 if i == 10 else 0.0 for i in range(118)], # Maps to Dance
        [1.0 if i == 45 else 0.0 for i in range(118)], # Maps to Exhaust
        [1.0 if i == 70 else 0.0 for i in range(118)], # Maps to Drama
        [1.0 if i == 90 else 0.0 for i in range(118)]  # Maps to Joy
    ]
    
    model, embedder = train_action_model(sample_texts, sample_targets, num_total_actions, epochs=500)
    
    # Inference
    test_text = ["You want to dance with me?"]
    test_emb = embedder.encode(test_text, convert_to_tensor=True)
    with torch.no_grad():
        prediction = model(test_emb)
        predicted_action_idx = torch.argmax(prediction).item()
        print(f"Predicted Action Index for '{test_text[0]}': {predicted_action_idx}")
