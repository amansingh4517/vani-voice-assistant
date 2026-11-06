# Import functions from your isolated modules
from .fs_tools import create_file, read_file, list_directory
from .sys_tools import exit_system

# The unified dictionary for Engine execution
TOOL_REGISTRY = {
    'create_file': create_file,
    'read_file': read_file,
    'list_directory': list_directory,
    'exit_system': exit_system
}

# The unified schema list for Ollama
AVAILABLE_TOOLS_LIST = list(TOOL_REGISTRY.values())