<p align="center">
  <img src="assets/logo.svg" alt="Vani Logo" width="200"/>
</p>

<h1 align="center">Vani Voice Assistant</h1>

<p align="center"><b>Your personal voice assistant, running entirely on your Mac.</b></p>

<p align="center">
  <img src="assets/banner.svg" alt="Vani Voice Assistant Banner" width="850"/>
</p>

<p align="center">
  <b>Fully local voice assistant for macOS.</b> Wake-word detection, speech-to-text, LLM reasoning, 71 macOS tools, and neural text-to-speech.<br>
  Built on MLX, Ollama, openWakeWord, and Apple Silicon.
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#available-tools">Available Tools</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13+"/>
  <img src="https://img.shields.io/badge/macOS-Apple%20Silicon-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macOS"/>
  <img src="https://img.shields.io/badge/Ollama-qwen3.5:9b-1a1a2e?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/mlx--audio-STT%20%2B%20TTS-FF6F00?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHRleHQgeD0iNCIgeT0iMTgiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IndoaXRlIj7imqE8L3RleHQ+PC9zdmc+" alt="MLX Audio"/>
  <img src="https://img.shields.io/badge/tools-71-28a745?style=for-the-badge" alt="71 Tools"/>
  <img src="https://img.shields.io/badge/runs-100%25%20local-blueviolet?style=for-the-badge" alt="100% Local"/>
</p>

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Available Tools](#available-tools)
- [Configuration](#configuration)
- [Testing & Linting](#testing--linting)
- [Requirements](#requirements)
- [Acknowledgements](#acknowledgements)

## Features

- **100% Local & Private** — no API keys, no cloud inference; runs on Apple Silicon unified memory
- **On-Device Wake Word** — passive acoustic keyword spotting (`"hey jarvis"`) via `openwakeword` (`onnxruntime`), keeping VAD and Whisper idle until triggered
- **Conversational Follow-up Window** — after Vani replies, stay in active listening for `FOLLOW_UP_SECONDS` (`8` s) with no wake word needed for follow-ups or confirmations
- **Unified Audio Engine** — speech-to-text (`whisper-large-v3-turbo-asr-fp16`) and neural text-to-speech (`Kokoro-82M-bf16`) powered by `mlx-audio`
- **Silero VAD + Ring Buffer** — 16 kHz voice activity detection with a ~0.5 s pre-speech buffer so initial words are never clipped
- **Agentic Tool Calling** — local Ollama (`qwen3.5:9b`) reasoning with up to 6 chained tool calls per turn
- **71 macOS Tools** — apps, files, Spotlight search, web, YouTube Music, system controls, iMessage, Calendar, Reminders, Notes, and more
- **Extensible & Safe** — `pkgutil.walk_packages` auto-discovery, `CommandRunner` abstraction, path protection, shell blocklist, and confirmation gates

## Installation

### Prerequisites

- macOS on Apple Silicon (M1/M2/M3/M4)
- Python 3.13+
- [Ollama](https://ollama.com) installed and running

### 1. Pull the LLM model

```bash
ollama pull qwen3.5:9b
```

### 2. Clone and install

```bash
git clone https://github.com/amansingh4517/vani-voice-assistant.git
cd vani-voice-assistant
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development (testing and linting):

```bash
pip install -e ".[dev]"
```

### 3. Grant macOS permissions

Go to **System Settings → Privacy & Security** and grant your terminal:

- **Microphone** — for wake-word and voice input
- **Accessibility** — for keyboard control and app management
- **Automation** — for AppleScript-based tools (Calendar, Music, Reminders, etc.)

## Quick Start

### Running the assistant

```bash
python -m vani
```

You can also use the installed console script `vani` or `make run`.

### Wake Word & Voice Flow

1. On startup, Vani loads the wake-word, Silero VAD, Whisper, and Kokoro models (the first run caches model weights locally).
2. Vani waits passively in wake-word mode (`[EAR] Waiting for wake word...`).
3. Say **"hey jarvis"** to wake Vani, then speak your command within 6 seconds (`WAKE_GRACE_SECONDS`).
4. After Vani replies, she stays in active follow-up mode for **8 seconds** (`FOLLOW_UP_SECONDS`), so you can ask a follow-up or confirm an action without repeating the wake word.
5. If no speech occurs within `FOLLOW_UP_SECONDS`, Vani returns to passive wake-word listening.
6. Say **"exit"**, **"quit"**, **"stop"**, **"goodbye"**, or **"bye"** to shut down.

### Example commands

```
"Hey Jarvis... what's the weather like today?"
"Play Starboy"
"Open Google Chrome and search for MLX Audio"
"Set a timer for 5 minutes"
"What's my battery percentage?"
"Create a calendar event for tomorrow at 3pm called Team Standup"
"Organize my Downloads folder"
"Turn on dark mode and set the volume to 50"
```

## Documentation

- [Architecture & Pipeline](docs/architecture.md)
- [Wake Word Detection & Tuning](docs/wake-word.md)
- [Adding a New Tool](docs/adding-tools.md)
- [Safety & Guardrails](docs/safety.md)

## Project Structure

```
vani-voice-assistant/
├── pyproject.toml                  # Package config, dependencies, pytest & ruff settings
├── Makefile                        # run, test, lint shortcuts
├── LICENSE                         # MIT License
├── .env.example                    # Optional environment variable reference
├── docs/
│   ├── architecture.md
│   ├── adding-tools.md
│   ├── safety.md
│   └── wake-word.md
├── scripts/
│   └── wake_debug.py               # Live wake-word score & mic peak meter
├── src/vani/
│   ├── __init__.py
│   ├── __main__.py                 # `python -m vani` entrypoint
│   ├── app.py                      # Main loop, exit handling, follow-up state
│   ├── config.py                   # LLM, VAD, wake-word, and TTS settings
│   ├── agent/
│   │   ├── engine.py               # Ollama chat + tool execution loop
│   │   ├── history.py              # Conversation history trimming
│   │   └── prompt.py               # Vani persona and instructions
│   ├── audio/
│   │   ├── wake.py                 # WakeWordDetector (openWakeWord)
│   │   ├── listener.py             # Mic stream, wake gate, Silero VAD, Whisper STT
│   │   ├── speaker.py              # Kokoro TTS via mlx-audio
│   │   └── speaker_fallback.py     # macOS `say` fallback
│   └── tools/
│       ├── __init__.py             # Auto-discovers tools via pkgutil.walk_packages
│       ├── advanced.py             # Raw shell & AppleScript tools
│       ├── core/                   # @tool registry, CommandRunner, paths, dates, safety
│       ├── system/                 # apps, power, network, system_info, sound_display
│       ├── files/                  # files, file_search, organizer, archives
│       ├── comms/                  # messaging, calendar_tools, reminders_notes
│       ├── media/                  # media, web
│       ├── desktop/                # desktop_utils, input_control
│       └── utility/                # calculator, exit
└── tests/
    ├── conftest.py                 # Shared FakeRunner fixture
    ├── agent/test_history.py
    ├── audio/test_wake.py
    └── tools/                      # Split unit tests by tool area
```

## Available Tools

- **System (`system/`)**: `open_app` · `quit_app` · `force_quit_app` · `list_running_apps` · `get_frontmost_app` · `open_system_settings` · `lock_screen` · `sleep_display` · `sleep_mac` · `restart_mac` · `shut_down_mac` · `set_wifi` · `set_bluetooth` · `get_ip_address` · `get_battery_status` · `get_system_info` · `get_disk_usage` · `get_current_datetime` · `get_volume` · `set_volume` · `change_volume` · `set_mute` · `change_brightness` · `set_dark_mode` · `toggle_dark_mode`
- **Files (`files/`)**: `list_directory` · `get_file_info` · `read_text_file` · `write_text_file` · `append_text_file` · `create_folder` · `move_path` · `copy_path` · `rename_path` · `delete_path` · `empty_trash` · `find_files` · `search_in_files` · `open_path` · `open_file_with_app` · `reveal_in_finder` · `organize_folder` · `zip_path` · `unzip_file`
- **Comms (`comms/`)**: `send_imessage` · `compose_email` · `create_calendar_event` · `get_calendar_events` · `create_reminder` · `list_reminders` · `create_note`
- **Media (`media/`)**: `play_song` · `music_control` · `get_now_playing` · `play_song_in_music` · `open_url` · `web_search` · `search_on_youtube` · `get_weather`
- **Desktop (`desktop/`)**: `get_clipboard` · `set_clipboard` · `show_notification` · `speak` · `take_screenshot` · `set_timer` · `type_text` · `press_keys`
- **Utility & Advanced**: `calculate` · `exit_system` · `run_shell_command` · `run_applescript`

## Configuration

Edit [`src/vani/config.py`](src/vani/config.py) to customize behavior:

```python
MAIN_MODEL = "qwen3.5:9b"
LLM_TEMPERATURE = 0.8
LLM_TOP_P = 0.9
LLM_REPEAT_PENALTY = 1.15

WAIT_TIME_SECONDS = 1.5        # silence before transcribing

WAKE_MODEL = "hey_jarvis"      # openWakeWord pretrained model
WAKE_THRESHOLD = 0.35          # raise if false triggers, lower if it misses you
FOLLOW_UP_SECONDS = 8          # no wake word needed for this long after a reply

TTS_MODEL = "mlx-community/Kokoro-82M-bf16"
TTS_VOICE = "hf_alpha"
TTS_LANG_CODE = "h"
TTS_SPEED = 1.0
```

## Testing & Linting

All unit tests run cross-platform without microphone hardware or macOS commands:

```bash
pytest
# or: make test
```

Lint with Ruff:

```bash
ruff check src tests scripts
# or: make lint
```

## Requirements

| Package | Purpose |
| --- | --- |
| `ollama` | Local LLM inference client |
| `mlx-audio` | Whisper STT & Kokoro TTS on Apple Silicon |
| `openwakeword` | Acoustic keyword spotting (wake-word detection) |
| `onnxruntime` | ONNX inference runtime for `openwakeword` |
| `silero-vad-lite` | Voice activity detection |
| `sounddevice` | Microphone audio capture |
| `soundfile` | WAV file I/O |
| `numpy` | Audio array processing |
| `misaki` | Phonemizer for Kokoro TTS |
| `num2words` | Number-to-word conversion for TTS |
| `spacy` | NLP dependency required by TTS pipeline |

## Acknowledgements

- [Ollama](https://ollama.com) — local LLM inference
- [MLX](https://github.com/ml-explore/mlx) — Apple Silicon ML framework
- [MLX Audio](https://github.com/Blaizzy/mlx-audio) — Whisper & Kokoro on MLX
- [openWakeWord](https://github.com/dscripka/openWakeWord) — on-device wake-word detection
- [Silero VAD](https://github.com/snakers4/silero-vad) — voice activity detection
- [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) — neural text-to-speech

---

<p align="center">Built with ❤️ on Apple Silicon</p>
