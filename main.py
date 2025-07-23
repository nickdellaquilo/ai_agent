import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info

if len(sys.argv) < 2:
    print("ERROR: No input message")
    exit(1)

model_name = "gemini-2.0-flash-001"
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
user_prompt = sys.argv[1]
verbose = False

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

if len(sys.argv) > 2:
    verbose = ("--verbose" in sys.argv)

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model = model_name,
    contents = messages,
    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt)
    )

if response.function_calls:
    for function_call_part in response.function_calls:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
else:
    print(response.text)

if verbose:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")