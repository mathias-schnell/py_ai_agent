from pathlib import Path
from google import genai
from google.genai import types

def get_files_info(working_directory, directory=None):
    working_directory = Path(working_directory).resolve()
    # Treat None as referring to the working directory itself
    target_directory = (working_directory / (directory or ".")).resolve()

    # Prevent access outside the working directory
    if working_directory not in target_directory.parents and working_directory != target_directory:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not target_directory.is_dir():
        return f'Error: "{target_directory}" is not a directory'

    try:
        dir_contents = ""
        for item in target_directory.iterdir():
            file_size = item.stat().st_size
            is_dir = item.is_dir()
            dir_contents += f"- {item.name}: file_size={file_size} bytes, is_dir={is_dir}\n"
    except Exception as e:
        return f'Error: {e}'

    return dir_contents

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)