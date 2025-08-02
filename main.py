import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import available_functions, call_function

def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        exit(1)

    #if len(sys.argv) > 2:
    verbose = ("--verbose" in sys.argv)

    user_prompt = sys.argv[1]

    if verbose:
        print(f"User prompt: {user_prompt}")

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.0-flash-001"

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    for i in range(20):
        try:
            #print(f"DEBUG: Messages: {messages}")
            response_text = generate_content(client, messages, model_name, verbose)
            if response_text:
                print("Final response:")
                print(response_text)
                break
        except ConnectionError:
            print("Error: Connection lost. Wait a moment and try again.")
        except TimeoutError:
            print("Connection timed out, trying again...")
        except KeyboardInterrupt:
            print("Request cancelled by user.")
            break
            

def generate_content(client, messages, model_name, verbose):
    response = client.models.generate_content(
        model = model_name,
        contents = messages,
        config = types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt)
    )

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
    if not response.function_calls:
        return response.text

    for candidate in response.candidates:
        messages.append(candidate.content)

    function_responses = []
    #print(f"DEBUG: Found {len(response.function_calls)} function calls")
    for function_call_part in response.function_calls:
        #print(f"DEBUG: About to call function: {function_call_part.name}")
        function_call_result = call_function(function_call_part, verbose)
        function_name = function_call_part.name
        #print(f"DEBUG: Function call completed")
        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
        ):
            raise Exception("empty function call result")
        result_data = function_call_result.parts[0].function_response.response
        if verbose:
            if isinstance(result_data, dict) and 'result' in result_data:
                print(f"-> {result_data['result']}")
            else:
                print(f"-> {result_data}")
        
        function_responses.append(function_call_result.parts[0])

    if not function_responses:
        raise Exception("no function responses generated, exiting.")

    #messages.append(types.Content(role="tool", parts=function_responses))
    messages.append(types.Content(
        role="model", parts=[types.Part(
            function_response=types.FunctionResponse(
                name=function_name,
                response=result_data
            )
        )]
    ))

if __name__ == "__main__":
    main()