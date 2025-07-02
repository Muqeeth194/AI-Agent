from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import subprocess
import os

load_dotenv()

client = OpenAI()

def get_weather(city: str):
    try:
        url = f'https://wttr.in/{city}?format=%C+%t'
        response = requests.get(url)

        if response.status_code == 200:
            return f'Weather of {city} is {response.text}.'
        else:
            return f'Could not get the weather of the {city}'
    except Exception as e:
        return f'Erro getting weather: {str(e)}'

def run_command(cmd: str):
    try:
        # safe_commands = ['ls', 'pwd', 'whoami', 'date', 'mkdir', 'touch', 'cat', 'echo']
        # command_parts = cmd.split()

        # if not command_parts or command_parts[0] not in safe_commands:
        #     return f"Command '{cmd}' connot be executed for security reasons."

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return f"Sucess: {result.stdout.strip()}"
        else:
            return f"Error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error running command: {str(e)}"
    
def create_file(input_data):
    """Create a file with optional content"""
    try:
        
        # Handle both string and dict inputs
        if isinstance(input_data, str):
            # If it's a string, try to parse as JSON
            try:
                data = json.loads(input_data)
            except:
                # If not JSON, treat as filename with empty content
                data = {"filename": input_data, "content": ""}
        else:
            data = input_data
        
        filename = data.get("filename", "")
        content = data.get("content", "")
        
        if not filename:
            return "Error: filename is required"
        
        # Security: only allow certain file types and reasonable names
        allowed_extensions = ['.txt', '.html', '.css', '.js', '.json', '.md', '.py']
        
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            return f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        # Prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return "Invalid filename - no paths allowed"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully created file: {filename}"
        
    except Exception as e:
        return f"Error creating file: {str(e)}"
    
def read_file(input_data):
    """Read content form a file"""
    
    try:
        if isinstance(input_data, str):
            filename = input_data
        else:
            filename = input_data.get("filename", "")
            
        if not os.path.exists(filename):
            return f"File '{filename}' does not exists."
        
        with open(filename, "r", encoding='utf-8') as f:
            content = f.read()
            
        return f"Content of {filename}: \n{content}"
    
    except Exception as e:
        return f"Error reading file {str(e)}"
            
        

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_file": create_file,
    "read_file": read_file,
}

SYSTEM_PROMPT = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes safe linux command as a string and executes the command and returns the output after executing it.
    - "create_file": Takes filename and content, creates the file
    - "read_file": Takes filename, returns file content

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

"""

def main():

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    print("🤖 AI Agent is ready! Type 'quit' to exit")

    while True:

        try: 

            query = input("\n> ").strip()

            if query.lower() in ['quit', 'exit']:
                print("GoodBye! 👋")
                break

            if not query:
                continue

            messages.append({"role":"user", "content":query})

            while True:
                response = client.chat.completions.create(
                    model= "gpt-4.1",
                    response_format= {"type": "json_object"},
                    messages = messages
                )

                ai_response = response.choices[0].message.content
                messages.append({"role": "assistant", "content": ai_response})

                try:
                    parsed_response = json.loads(ai_response)
                except json.JSONDecodeError:
                    print("❌ AI response was not valid JSON")
                    break
                
                step = parsed_response.get("step")
                
                if step == "plan":
                    print(f'🧠: {parsed_response.get("content")}')
                    continue

                elif step == "action":
                    tool_name = parsed_response.get("function")
                    tool_input = parsed_response.get("input")

                    print(f'🛠️ Using tool: {tool_name} with input: {tool_input}')

                    if tool_name in available_tools:
                        output = available_tools[tool_name](tool_input)
                        messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                        continue
                    else:
                        print(f"❌ Tool {tool_name} not found")
                        break

                elif step == "output":
                    print(f'🤖: {parsed_response.get("content")}')
                    break
                
                else:
                    print(f"❌ Unknown step: {step}")
                    break

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()