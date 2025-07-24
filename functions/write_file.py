import os
from config import MAX_CHARS
from google.genai import types

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_file_path):
        directory = os.path.dirname(abs_file_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                return f'Error creating directory "{directory}": {e}'
    with open(abs_file_path, "w") as f:
        try:
            f.write(content)
        except Exception as e:
            return f'Error writing content: {e}'
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Creates or overwrites a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path of the file to create or overwrite, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The text to be written into the specified file.",
            )
        },
    ),
)