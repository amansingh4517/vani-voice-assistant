import os

def create_file(file_path: str, content: str) -> str:
    """Creates a new file with the given content. Use to write code or save data."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Success: Created {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"



def read_file(file_path: str) -> str:
    """Reads the contents of a file. Use this to inspect code or read logs before modifying them."""
    try:
        if not os.path.exists(file_path):
            return f"Error: The file {file_path} does not exist."
        with open(file_path, 'r') as f:
            return f"File contents of {file_path}:\n\n{f.read()}"
    except Exception as e:
        return f"Error reading file: {str(e)}"



def list_directory(dir_path: str = ".") -> str:
    """Lists all files and folders in a given directory path. Defaults to current directory."""
    try:
        if not os.path.exists(dir_path):
            return f"Error: Directory {dir_path} not found."
        items = os.listdir(dir_path)
        return f"Contents of {dir_path}: " + ", ".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
