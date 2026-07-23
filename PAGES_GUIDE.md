# Pages & Navigation Guide

## 🏠 Main Pages

### 1. **Landing Page** (`/`)
- **File:** `index.html`
- **Purpose:** Welcome screen with quick access to all features
- **Features:**
  - Hero section with system info
  - Quick stats (sessions, time, memory)
  - Navigation to all major sections
  - CTA buttons for quick access

### 2. **Chat Interface** (`/chat`)
- **File:** `bayazid_chat.html`
- **Purpose:** Main chat with Bayazid or Marin
- **Features:**
  - Agent switcher (BAYAZID ↔ MARIN)
  - Message history
  - Voice synthesis toggle
  - File upload support
  - Real-time streaming responses

### 3. **Research Hub** (`/research-hub`)
- **File:** `research_hub.html` ✅ FIXED
- **Purpose:** Search for PDFs and academic resources
- **Features:**
  - Search bar with Enter key support
  - Grid-based result cards
  - Error handling with messages
  - Loading spinner
  - Mobile responsive

### 4. **Knowledge Hub** (`/knowledge-hub`)
- **File:** `knowledge_hub.html`
- **Purpose:** Manage and teach topics
- **Features:**
  - Topic management
  - Quiz generation
  - Study plans
  - Agent switcher (Bayazid/Marin)

### 5. **Vault Explorer** (`/vault`)
- **File:** `vault_explorer.html` ✅ VERIFIED
- **Purpose:** Private file storage for both agents
- **Features:**
  - Bayazid's Vault (left sidebar)
  - Marin's Vault (left sidebar)
  - File viewer
  - Delete functionality
  - Category organization

### 6. **Profile** (`/profile`)
- **File:** `profile.html`
- **Purpose:** User settings and preferences
- **Features:**
  - User info
  - Settings management
  - Navigation to other pages

### 7. **Arena** (`/arena`)
- **File:** `arena_chat.html`
- **Purpose:** Bayazid vs Marin debate/judge system
- **Features:**
  - Debate mode
  - Judge mode
  - Real-time responses
  - History tracking

### 8. **Terminal Log** (`/cmd/log`)
- **File:** `terminal_log.html`
- **Purpose:** View command execution logs
- **Features:**
  - Command history
  - Refresh button
  - Back to chat link

---

## 🔗 Navigation Map

```
Landing Page (/)
├── /chat → Chat Interface
│   ├── Switch to Marin
│   ├── /research-hub
│   ├── /knowledge-hub
│   ├── /vault
│   ├── /profile
│   └── /arena
├── /research-hub → Research Hub
│   └── Back to Chat
├── /knowledge-hub → Knowledge Hub
│   ├── Bayazid/Marin switcher
│   └── Back to Chat
├── /vault → Vault Explorer
│   ├── Bayazid's Vault
│   ├── Marin's Vault
│   └── Back to Chat
├── /profile → Profile
│   ├── HOME
│   ├── RESEARCH
│   └── HUB
└── /arena → Arena
    └── Back to Chat
```

---

## 🎯 Quick Access URLs

| Page | URL | Shortcut |
|------|-----|----------|
| Landing | `http://localhost:5069/` | Home |
| Bayazid Chat | `http://localhost:5069/chat` | Main chat |
| Marin Chat | `http://localhost:5069/chat?agent=marin` | Marin mode |
| Research | `http://localhost:5069/research-hub` | Search PDFs |
| Knowledge | `http://localhost:5069/knowledge-hub` | Manage topics |
| Vault | `http://localhost:5069/vault` | File storage |
| Profile | `http://localhost:5069/profile` | Settings |
| Arena | `http://localhost:5069/arena` | Debate mode |
| Logs | `http://localhost:5069/cmd/log` | Command history |

---

## 🚀 Starting the Server

```bash
cd /home/sword/Documents/BayazidxMarin
source .venv/bin/activate
python run_all.sh
```

Then open: **http://localhost:5069**

---

## ⚡ Tips

1. **Fast Navigation:** Use the nav links at the top of each page
2. **Agent Switching:** Click BAYAZID/MARIN buttons in chat
3. **Search:** Press Enter in research hub to search
4. **Vault:** Both agents have separate vaults (left sidebar)
5. **Mobile:** All pages work on mobile devices
6. **Offline:** Research hub needs internet for PDF search

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Pages load slowly | Ensure Ollama is running |
| Research returns no results | Check internet connection |
| Chat not responding | Restart Ollama service |
| Vault shows no files | Files are stored per agent |
| Mobile layout broken | Clear browser cache |

---

## 📝 Notes

- All pages use consistent dark theme
- Animations are smooth (0.2-0.3s transitions)
- Mobile responsive (works on all screen sizes)
- XSS protection on all user inputs
- Real-time updates via WebSocket/fetch
