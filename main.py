import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python import schema_run_python_file
from functions.call_function import call_function

load_dotenv()

verbose = False
if "--verbose" in sys.argv:
    verbose = True

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash-001"
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

if len(sys.argv) > 1:
    messages = [
        types.Content(role="user", parts=[types.Part(text=sys.argv[1])]),
    ]

    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
else:
    raise Exception("no input provided")
    sys.exit(1)

if response.function_calls is not None and len(response.function_calls) > 0:
    for func_call in response.function_calls:
        result = call_function(func_call, verbose)
        fatal_ex = False

        if not hasattr(result, "parts"):
            fatal_ex = True
        if not isinstance(result.parts, list) or len(result.parts) == 0:
            fatal_ex = True
        part = result.parts[0]
        if not hasattr(part, "function_response"):
            fatal_ex = True
        if not hasattr(part.function_response, "response"):
            fatal_ex = True
        
        if fatal_ex:
            raise Exception("Fatal Exception")
        elif verbose:
            print(f"-> {result.parts[0].function_response.response}")
        
        


else:
    print(response.text)
if verbose:
    print(f"User prompt: {sys.argv[1]}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")