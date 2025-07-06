from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import subprocess
import os
import time

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
        # if '..' in filename or '/' in filename or '\\' in filename:
        #     return "Invalid filename - no paths allowed"
        
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
    
def handle_clarification_step(paresed_response, messages):
    """Handle clarification steps in conversation"""
    if paresed_response.get("step") == "clarify":
        question = paresed_response.get("question", "")
        content = paresed_response.get("content", "")
        
        print(f'🤖: {content}')
        if question:
            print(f'❓: {question}')
        return True
        
    return False

def create_react_app_smart(input_data):
    try: 
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
            except:
                # Extract app name from string if provided
                words = input_data.lower().split()
                app_name = "my-react-app"  # default
                
                # Look for app name patterns
                for i, word in enumerate(words):
                    if word in ["called", "named", "app"] and i + 1 < len(words):
                        app_name = words[i + 1]
                        break
                
                data = {"app_name": app_name}
        else:
            data = input_data
            
        
        app_name = data.get("app_name", "my-react-app")
        template = data.get("template", "react")
        
        app_name = app_name.replace(" ", "-").lower()
        
        # command
        cmd = f"npx create-vite@latest {app_name} --template {template} --javascript --yes"
        
        print(cmd)
        
        
        # Run non-interactive command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("command executed successfully")
            return f"Successfully created React app '{app_name}' with Vite! Run 'cd {app_name} && npm install && npm run dev' to start."
        else:
            print("Error executing the command")
            return f"Error creating React app: {result.stderr.strip()}"
        
    except Exception as e:
        return f"Error: {str(e)}"
    
    
def run_react_app(input_data):
    
    try:
        
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
            except:
                # If it's just a string, treat it as the app name
                data = {"app_name": input_data}
        else:
            data = input_data
            
        app_name = data.get("app_name", "")
        
        if not app_name:
            return "Error: app_name is required"
        
        # Clean up app name (remove spaces, make lowercase)
        app_name = app_name.replace(" ", "-").lower()
        
        # Check if the app directory exists
        if not os.path.exists(app_name):
            return f"Error: App directory '{app_name}' does not exist. Please create the app first."
        
        if not os.path.isdir(app_name):
            return f"Error: '{app_name}' is not a directory."
        # Store current directory
        original_dir = os.getcwd()
        
        # navigate inside the provided app name folder.
        try:
            # Navigate to the app directory
            os.chdir(app_name)
            print(f"📁 Changed directory to: {os.getcwd()}")
            
            # Check if package.json exists
            if not os.path.exists("package.json"):
                return f"Error: No package.json found in '{app_name}'. This doesn't appear to be a Node.js project."
            
            # Step 1: Install dependencies
            print("📦 Installing dependencies with npm install...")
            cmd1 = "npm install"
            installation_result = subprocess.run(
                cmd1, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300  # Increased timeout for npm install
            )
            
            if installation_result.returncode != 0:
                return f"Error installing dependencies: {installation_result.stderr.strip()}"
            
            print("✅ Dependencies installed successfully!")
            
            # Step 2: Start the development server
            print("🚀 Starting development server...")
            cmd2 = "npm run dev"
            
            # For dev server, we need to run it without capture_output so it can display properly
            # But we need to handle it carefully since it runs indefinitely
            
            # Option 1: Run in background and return immediately
            dev_process = subprocess.Popen(
                cmd2,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait a bit to see if it starts successfully
            time.sleep(3)
            
            # Check if process is still running (indicates successful start)
            if dev_process.poll() is None:
                # Process is running, try to get some initial output
                try:
                    # Read initial output to check for success indicators
                    output_lines = []
                    start_time = time.time()
                    
                    while time.time() - start_time < 5:  # Wait up to 5 seconds for output
                        try:
                            line = dev_process.stdout.readline()
                            if line:
                                output_lines.append(line.strip())
                                print(f"📺 {line.strip()}")
                                
                                # Check for success indicators
                                if any(indicator in line.lower() for indicator in ['local:', 'localhost', 'ready', 'dev server']):
                                    break
                        except:
                            break
                        time.sleep(0.1)
                    
                    return f"✅ App '{app_name}' is running successfully! Development server started.\n" + \
                            f"Initial output:\n" + '\n'.join(output_lines[:10])  # Show first 10 lines
                    
                except Exception as e:
                    return f"✅ App '{app_name}' appears to be running (process started successfully)"
                    
            else:
                # Process ended, something went wrong
                stdout, stderr = dev_process.communicate()
                return f"Error starting development server: {stderr or stdout}"
                
        finally:
            # Always return to original directory
            os.chdir(original_dir)
            
    except subprocess.TimeoutExpired:
        return "Error: Installation timed out (took more than 5 minutes)"
    except FileNotFoundError:
        return "Error: npm not found. Please make sure Node.js and npm are installed."
    except PermissionError:
        return f"Error: Permission denied accessing '{app_name}' directory"
    except Exception as e:
        return f"Error: {str(e)}"
    
def stop_react_app(input_data):
    """
    Stop running React app (kills npm processes)
    """
    try:
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
            except:
                data = {"app_name": input_data}
        else:
            data = input_data
            
        app_name = data.get("app_name", "")
        
        # Kill npm processes (works on Unix-like systems)
        try:
            if os.name != 'nt':  # Unix/Linux/Mac
                subprocess.run("pkill -f 'npm run dev'", shell=True)
                subprocess.run("pkill -f 'vite'", shell=True)
            else:  # Windows
                subprocess.run("taskkill /f /im node.exe", shell=True)
                
            return f"✅ Stopped development servers for React apps"
            
        except Exception as e:
            return f"Error stopping app: {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"
        

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_file": create_file,
    "read_file": read_file,
    "create_react_app_smart" : create_react_app_smart,
    "run_react_app" :run_react_app,
    "stop_react_app": stop_react_app,
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
    - Be conversational and helpful

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
        "question": "question to ask user (only for clarify step)"
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes safe linux command as a string and executes the command and returns the output after executing it.
    - "create_file": Takes filename and content, creates the file
    - "read_file": Takes filename, returns file content
    - "create_react_app_smart": Takes JSON with app_name and optional template
    - "run_react_app": Takes the name of the web app as the input and executes the command to run the applcation.
    - "stop_react_app": Takes the name of the web app as the input and executes the command to stop the applcation.

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

    Examples:
    User: "Create a React app"
    Output: {{"step": "clarify", "content": "I can create a React app for you using vite!", "question": "What would you like to name your app? (I'll use 'my-react-app' if you don't specify)"}}

    User: "Create a React app called portfolio"
    Output: {{"step": "plan", "content": "I'll create a React app named 'portfolio' using Vite"}}
    Output: {{ "step": "plan", "content": "From the available tools I should call create_react_app_smart" }}
    Output: {{"step": "action", "function": "create_react_app_smart", "input": "{{\\"app_name\\": \\"portfolio\\", \\"template\\": \\"react\\"}}""}}
    
    User: "Run the react app"
    Output: {{"step: "plan", "content": "The user wants to run the react application"}}
    Output: {{"step: "plan", "content": "From the available tools I should call run_react_app"}}
    Output: {{ "step": "action", "function": "run_react_app", "input": "my-react-app" }}
    Output: {{ "step": "observe", "output": "Web app depedencies are installed and application started running" }}
    Output: {{ "step": "output", "content": "The 'my-react-app' application is running. Please use the local URL: 'http://localhost:5173/' to access the application" }}
    
    User: "Stop the react app"
    Output: {{"step: "plan", "content": "The user wants to stop the react application"}}
    Output: {{"step: "plan", "content": "From the available tools I should call stop_react_app"}}
    Output: {{ "step": "action", "function": "stop_react_app", "input": "my-react-app" }}
    Output: {{ "step": "observe", "output": "Application is stopped" }}
    Output: {{ "step": "output", "content": "The 'my-readt-app' application is stoppped now." }}
    
     
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
                
                 # Handle clarification step
                if handle_clarification_step(parsed_response, messages):
                    break  # Wait for user input
                
                if step == "plan":
                    print(f'🧠: {parsed_response.get("content")}')
                    continue

                elif step == "action":
                    tool_name = parsed_response.get("function")
                    tool_input = parsed_response.get("input")

                    print(f'🛠️ Using tool: {tool_name} with input: {tool_input}')
                    
                    print(f"tool name: {tool_name}")

                    if tool_name in available_tools:
                        output = available_tools[tool_name](tool_input)
                        print(f'output: {output}')
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