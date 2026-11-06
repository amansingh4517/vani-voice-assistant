# config.py

# --- AI MODEL CONFIGURATION ---
# The fast, lightweight model that stays in memory to route tools
ROUTER_MODEL = 'llama3.2'

# The heavy-duty model spun up dynamically for writing scripts
MAIN_MODEL = 'qwen3.5:9b'

# --- AUDIO CONFIGURATION ---
WAIT_TIME_SECONDS = 2.5