from pathlib import Path
from google import genai
from google.genai import types
import subprocess
import sys

def run_python_file(working_directory, file_path):
    working_directory = Path(working_directory).resolve()
    target_path = (working_directory / file_path).resolve()
    result_str = ""

    # Prevent access outside the working directory
    if working_directory not in target_path.parents and working_directory != target_path:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not target_path.exists():
        return f'Error: File "{file_path}" not found.'
    
    if target_path.suffix.lower() != ".py":
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        result = subprocess.run([sys.executable, str(target_path)], capture_output=True, text=True, timeout=30)

        if result.stdout == '' and result.stderr == '':
            result_str += "No output produced.\n"
        else:
            result_str += "STDOUT:" + result.stdout + "\n"
            result_str += "STDERR:" + result.stderr + "\n"
        if result.returncode != 0:
            result_str += "Process exited with code " + str(result.returncode) + "\n"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    return result_str

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the Python file at the given file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file, relative to the working directory.",
            ),
        },
    ),
)