import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

if len(sys.argv) < 2:
    print("ERROR: No input message")
    exit(1)

model_name = "gemini-2.0-flash-001"
system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'
user_prompt = sys.argv[1]
verbose = False

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
    config = types.GenerateContentConfig(system_instruction=system_prompt),
    )



print(response.text)

if verbose:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")