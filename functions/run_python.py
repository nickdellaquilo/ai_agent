import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    if not abs_file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    args = ['python3', abs_file_path] + args
    try:
        completed_process = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, timeout = 30, text = True)
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        returncode = completed_process.returncode
        result = ''
        # For successful runs, combine stdout and stderr since test frameworks use stderr
        if returncode == 0:
            output = stdout + stderr
            return output.strip() if output else 'No output produced.'
        if returncode != 0:
            result += f'Process exited with {returncode}\n'
        if result == '':
            return 'No output produced.'
        return result
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file with optional arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to the Python file to be run, relative to the working directory.",
            ),
        },
    ),
)