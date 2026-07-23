# AI Debate & Research Platform

## Our Mission
The core mission of this platform is to **generate high-quality synthetic chat data to train and fine-tune our VRM models** (like Marin). By simulating deep, multi-character debates and conversations, we can map nuanced texts to complex physical animations, and brainstorm better ideas through AI-driven discussion and research.

## Overview
Welcome to the AI Debate Simulator and Research Platform! This repository serves two main purposes:
1. **Multi-Agent Simulation**: Generating synthetic conversational datasets by making different LLM personas talk to each other.
2. **Research & RAG Operations**: Providing tools for PDF downloading, news harvesting, and RAG (Retrieval-Augmented Generation) processing to enhance agent knowledge.

## Project Structure

### The Debate Simulator
* `app.py`: The core Flask and LangChain application that orchestrates the AI debates.
* `templates/index.html`: The UI for selecting characters and topics, featuring dynamic avatar loading.
* `images/`: The folder containing your GennyAI/Character `.png` cards.
* `extract_chunks.py`: A utility script that extracts hidden system prompts and personalities directly from your character PNG files.
* `action_embedder.py`: A deep learning script for one-hot encoding conversational data to 118 distinct VRM animations.

### Research & Data Tools
* `rag_server.py` & `rag/`: The Retrieval-Augmented Generation engine.
* `tools/`: Specialized modules for automated research (News Harvester, PDF Downloader).
* `database.py` & `storage/`: Database handlers and `.db` files that store conversation history, which can be utilized to fine-tune Marin in the future.

## How to Run the Debate Simulator

1. Install the required dependencies:
   ```bash
   pip install flask langchain langchain-openai sentence-transformers torch Pillow
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5050`. You will see all characters loaded from the `images/` directory.

## Adding New Characters
To add new characters to the debate, simply drop a Character PNG (e.g., from SillyTavern/GennyAI) into the `images/` folder, and run:
```bash
python extract_chunks.py
```
This will automatically parse their hidden system prompt metadata and register them in the simulation database.
