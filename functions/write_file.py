from pathlib import Path
from google import genai
from google.genai import types

def write_file(working_directory, file_path, content):
    working_directory = Path(working_directory).resolve()
    target_path = (working_directory / file_path).resolve()

    # Prevent access outside the working directory
    if working_directory not in target_path.parents and working_directory != target_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    try:
        target_path.write_text(content)
    except Exception as e:
        return f'Error: {e}'

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file. Overwrites existing content if the file already exists. Constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The file's contents.",
            ),
        },
    ),
)