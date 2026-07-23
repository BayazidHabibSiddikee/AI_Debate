# BayazidxMarin Quick Start

## ✅ Setup Complete
- ✓ New venv created at `.venv/`
- ✓ All dependencies installed
- ✓ Both Bayazid and Marin ready to execute

## 🚀 Run Commands

### Option 1: Using activation script
```bash
source /home/sword/Documents/BayazidxMarin/activate.sh
python run_all.sh
```

### Option 2: Direct activation
```bash
cd /home/sword/Documents/BayazidxMarin
source .venv/bin/activate
python run_all.sh
```

### Option 3: Run specific agent
```bash
source .venv/bin/activate
python run_bayazid.sh
```

## 📍 Access
- **URL:** http://localhost:5069
- **Bayazid:** Productivity/Learning agent
- **Marin:** Gaming/Creative agent

## ⚠️ Prerequisites
Before running, ensure:
1. **Ollama is running:**
   ```bash
   ollama serve
   ```
   (In another terminal)

2. **Models are pulled:**
   ```bash
   ollama pull gemma4:31b-cloud
   ollama pull qwen2.5:0.5b
   ```

## 📝 Notes
- Venv is isolated in `.venv/` directory
- Requirements updated with flexible versions
- All core imports verified working
