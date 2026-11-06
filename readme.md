# Local Multi-Agent Voice Assistant

A fully local, voice-controlled, multi-agent AI assistant built exclusively for macOS (Apple Silicon). This project uses a Router-Worker architecture to parse voice commands, execute operating system actions, and write complex code autonomously—with zero cloud dependencies and absolute privacy.

## 🏗 System Architecture
* **The Ear (Audio In):** `Faster-Whisper` combined with a Ring-Buffered `Silero VAD` to prevent pre-roll word clipping.
* **The Brain (Router):** `Llama 3.2 (3B)` running via Ollama. It analyzes intent and triggers tools with near-zero latency.
* **The Hands (Worker Swarm):** `Qwen 2.5 Coder (7B)` delegated for heavy-duty software engineering tasks.
* **The Voice (Audio Out):** Native macOS `say` API (zero-latency, zero-RAM footprint).

## 📋 Prerequisites
Since this heavily leverages local hardware acceleration, you will need:
1. **macOS** (Apple Silicon M-series highly recommended)
2. **Python 3.9+**
3. **[Ollama](https://ollama.com/)** installed and running on your machine.

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/amansingh4517/voice-assistant.git](https://github.com/amansingh4517/voice-assistant.git)
cd voice-assistant
```

**2. Set up the Python environment**
```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

**3. Download the Local AI Models (Ollama)**
The system requires two models to function in the multi-agent setup:
```bash
# The Router Model (Fast, low latency)
ollama pull llama3.2

# The Coder Model (Heavy-duty programming)
ollama pull qwen2.5-coder:7b
```

## 🎙️ Usage

Once your environment is active and Ollama is running in the background, simply execute the main loop:

```bash
python main.py
```

* Wait for the `[EAR] Listening...` prompt.
* Speak naturally. Try saying:
  * *"List the files in my directory."*
  * *"Write a python script that calculates the Fibonacci sequence and save it as math.py."*
  * *"Shut down."*

## 📁 Project Structure (SOLID Principles)
* `main.py`: The synchronous event loop (Central Nervous System).
* `engine.py`: The LLM logic and tool routing layer.
* `config.py`: Single source of truth for dynamic model swapping.
* `tools/`: Decoupled, modular tool execution.
  * `ear.py`: VAD and Speech-to-Text.
  * `voice.py`: Native macOS Text-to-Speech execution.
  * `coder.py`: Qwen 2.5 Worker handoff logic.
  * `fs_tools.py` & `sys_tools.py`: File system and OS lifecycle management.