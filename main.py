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

response_count = 0
max_responses = 20
verbose = False
if "--verbose" in sys.argv:
    verbose = True

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash-001"
system_prompt = """
You are a helpful AI coding agent with access to file system tools.

When a user asks a question about code or files, you should:
1. First use get_files_info to explore the current directory and see what files are available
2. Use get_file_content to read relevant files 
3. Analyze the code and provide a comprehensive answer

You have access to these tools:
- get_files_info: Lists files and directories in the current working directory
- get_file_content: Reads the contents of a specific file
- run_python_file: Executes Python files
- write_file: Creates or overwrites files

Always be proactive in using these tools to investigate and answer questions about the codebase.
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
    
    while(response_count < max_responses):
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )
        
        for candidate in response.candidates:
            messages.append(candidate.content)

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
                
                messages.append(result)
        else:
            print(response.text)
            break
        
        response_count += 1
else:
    raise Exception("no input provided")
    sys.exit(1)

if verbose:
    print(f"User prompt: {sys.argv[1]}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")