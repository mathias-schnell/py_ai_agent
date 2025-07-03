from pathlib import Path
from google import genai
from google.genai import types

def get_file_content(working_directory, file_path):
    working_directory = Path(working_directory).resolve()
    target_path = (working_directory / file_path).resolve()

    # Prevent access outside the working directory
    if working_directory not in target_path.parents and working_directory != target_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not target_path.is_file():
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        content = target_path.read_text()
        if len(content) > 10000:
            content = content[:10000] + f"[...File '{target_path.name}' truncated at 10000 characters]"
    except Exception as e:
        return f'Error: {e}'

    return content

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Displays the content of a file, truncated if above 10,000 characters long. Constrained to the working directory.",
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