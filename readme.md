# 🤖 JARVIS — Local macOS Voice Assistant

A fully local, JARVIS-style voice assistant for macOS built on Apple Silicon. It listens to your voice, thinks with a local LLM, controls your Mac with 60+ tools, and speaks back — all without sending a single byte to the cloud.

```
 🎙️ Listen  ──▶  🧠 Think  ──▶  ⚡ Act  ──▶  🔊 Speak
  (Whisper)      (Ollama)     (macOS)     (Kokoro)
```

## ✨ Features

- **Fully Local & Private** — All AI models run on-device via [MLX](https://github.com/ml-explore/mlx) and [Ollama](https://ollama.com). No API keys, no cloud dependencies.
- **Natural Voice Interaction** — Continuous listening with Silero VAD (voice activity detection) + MLX Whisper for transcription and Kokoro neural TTS for lifelike speech.
- **60+ macOS Control Tools** — App management, file operations, web search, media control, system settings, messaging, calendar, reminders, and more.
- **Agentic Tool Calling** — The LLM can chain up to 6 tool calls per turn to complete complex multi-step tasks.
- **Safety-First Design** — Path protection, shell command blocklist, and confirmation gates for destructive actions.
- **Extensible Architecture** — Drop a new Python file in `mac_tools/` with a `@tool` decorator and it's automatically discovered and available.

## 📋 Prerequisites

- **macOS** on Apple Silicon (M1/M2/M3/M4)
- **Python 3.13+**
- **[Ollama](https://ollama.com)** installed and running

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Voice Assistant"
```

### 2. Pull the LLM model

```bash
ollama pull qwen3.5:9b
```

### 3. Create a virtual environment & install dependencies

```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
pip install silero-vad-lite
```

### 4. Grant macOS permissions

Go to **System Settings → Privacy & Security** and grant your terminal:

| Permission       | Required For                          |
| ---------------- | ------------------------------------- |
| **Microphone**   | Voice input                           |
| **Accessibility** | Keyboard control, app management     |
| **Automation**   | AppleScript-based tools (Calendar, Music, etc.) |

### 5. Run

```bash
python main.py
```

The assistant will load the VAD, Whisper, and Kokoro models into memory (first run may take a moment to download), then start listening. Speak naturally and it will respond.

Say **"exit"**, **"quit"**, or **"stop"** to shut down.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  ear.py     │────▶│  main.py    │────▶│  engine.py   │────▶│  voice.py   │
│  (STT)      │     │  (loop)     │     │  (LLM+tools) │     │  (TTS)      │
│  Silero VAD │     │             │     │  Ollama chat  │     │  Kokoro MLX │
│  + Whisper  │     │             │     │  + tool exec  │     │             │
└─────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │   mac_tools/     │
                                    │  60+ tool funcs  │
                                    │  via @tool deco  │
                                    └──────────────────┘
```

| Component | File | Description |
| --------- | ---- | ----------- |
| **Entry Point** | `main.py` | Runs the listen → think → speak loop. Manages conversation history (last 8 turns) and handles exit logic. |
| **LLM Engine** | `engine.py` | Sends messages to Ollama with tool definitions. Executes tool calls in an agentic loop (max 6 steps) until the LLM produces a final text response. |
| **Speech-to-Text** | `tools/ear.py` | Captures microphone audio, detects speech with Silero VAD, and transcribes with MLX Whisper (`whisper-large-v3-turbo`). Uses a ring buffer to avoid clipping the start of speech. |
| **Text-to-Speech** | `tools/voice.py` | Synthesizes speech with Kokoro (`Kokoro-82M-bf16`) via MLX Audio. Strips markdown before synthesis. |
| **TTS Fallback** | `tools/voice2.py` | Falls back to the native macOS `say` command if needed. |
| **System Prompt** | `prompt.py` | Defines the JARVIS persona with dynamic date/time injection, speech-optimized output rules, and safety guidelines. |
| **Tool Registry** | `mac_tools/core/registry.py` | The `@tool` decorator and `ToolRegistry` class that powers auto-discovery. |
| **macOS Tools** | `mac_tools/*.py` | 60+ tool functions across 17 modules (see below). |

## 🛠️ Available Tools

| Category | Module | Tools |
| -------- | ------ | ----- |
| **Apps** | `apps.py` | Open, quit, force-quit apps; list running apps; open System Settings |
| **Files** | `files.py` | List, read, write, append, create, move, copy, rename, delete files & folders; empty trash |
| **File Search** | `file_search.py` | Find files by name/content (Spotlight), open files, reveal in Finder |
| **Web** | `web.py` | Open URLs, web search (Google/YouTube/Maps), weather |
| **Media** | `media.py` | Apple Music & Spotify control, now playing info |
| **Sound & Display** | `sound_display.py` | Volume, mute, brightness, dark mode |
| **System Info** | `system_info.py` | Battery, system info, disk usage, date/time |
| **Network** | `network.py` | Wi-Fi, Bluetooth, IP address |
| **Power** | `power.py` | Lock screen, sleep, restart, shut down |
| **Input Control** | `input_control.py` | Type text, press keyboard shortcuts |
| **Messaging** | `messaging.py` | Send iMessage, compose email |
| **Calendar** | `calendar_tools.py` | Create & list calendar events |
| **Reminders & Notes** | `reminders_notes.py` | Create reminders & notes, list reminders |
| **Calculator** | `calculator.py` | Safe math evaluation (AST-based, no `eval()`) |
| **Desktop Utilities** | `desktop_utils.py` | Clipboard, notifications, screenshots, timers |
| **Organizer** | `organizer.py` | Auto-sort folder contents by file type |
| **Archives** | `archives.py` | Zip & unzip files |
| **Advanced** | `advanced.py` | Raw shell commands (with blocklist) & AppleScript |

## ➕ Adding a New Tool

1. Create a new `.py` file in `mac_tools/` (or add to an existing one).
2. Import and use the `@tool` decorator:

```python
from mac_tools.core import tool, CommandRunner

@tool(
    category="my_category",
    confirm=False,  # Set True for destructive actions
)
def my_new_tool(runner: CommandRunner, arg1: str, arg2: int = 5) -> str:
    """One-line description for the LLM.

    Args:
        arg1: What this argument does.
        arg2: Optional argument with a default.
    """
    result = runner.run(["some", "command", arg1])
    return f"Done: {result.stdout}"
```

3. That's it — the tool is automatically discovered and made available to the LLM on the next run.

## 🔒 Safety

- **Path Protection** — System directories and top-level home folders (Desktop, Documents, etc.) cannot be deleted.
- **Shell Blocklist** — Dangerous commands like `sudo`, `rm -rf /`, `mkfs`, `dd`, and curl-pipe-to-shell patterns are blocked.
- **Confirmation Gates** — Destructive actions (delete, empty trash, restart, shutdown, send messages) require explicit user confirmation.
- **Tool Loop Limit** — Max 6 tool calls per turn to prevent infinite loops.
- **False Exit Prevention** — LLM exit signals are validated against actual keywords in the user's speech.

## ⚙️ Configuration

Edit [`config.py`](config.py) to change:

```python
MAIN_MODEL = 'qwen3.5:9b'     # Ollama model to use
WAIT_TIME_SECONDS = 2.5        # Silence duration before transcription triggers
```

## 🧪 Testing

Run the unit tests (cross-platform — no macOS required thanks to the `FakeRunner` abstraction):

```bash
python -m pytest mac_tools/tests/
```

## 📦 Dependencies

| Package | Purpose |
| ------- | ------- |
| `ollama` | Local LLM inference client |
| `mlx-audio` | Whisper STT & Kokoro TTS on Apple Silicon |
| `sounddevice` | Microphone audio capture |
| `soundfile` | WAV file I/O |
| `numpy` | Audio array processing |
| `misaki` | Phonemizer for Kokoro TTS |
| `num2words` | Number-to-word conversion for TTS |
| `silero-vad-lite` | Voice activity detection |
| `loguru` | Logging |

## 📄 License

This project is for personal use. See the repository for license details.

---

*Built with ❤️ on Apple Silicon — by Aman Singh*

