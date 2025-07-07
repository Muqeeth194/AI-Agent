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
        # allowed_extensions = ['.txt', '.html', '.css', '.js', '.json', '.md', '.py']
        
        # if not any(filename.endswith(ext) for ext in allowed_extensions):
        #     return f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        
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
    
def list_files(input_data):
    """List files in current directory or specified directory"""
    try:
        if isinstance(input_data, str):
            directory = input_data if input_data else "."
        else:
            directory = input_data.get("directory", ".")
        
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        return f"Files in {directory}: {', '.join(files)}"
    except Exception as e:
        return f"Error listing files: {str(e)}"
        

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_file": create_file,
    "read_file": read_file,
    "create_react_app_smart" : create_react_app_smart,
    "run_react_app" :run_react_app,
    "stop_react_app": stop_react_app,
    "list_files": list_files,
}

SYSTEM_PROMPT = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format exactly
    - Always perform one step at a time and wait for next input
    - Carefully analyze the user query and current app state
    - Be conversational and helpful
    - For complex transformations, break into logical phases
    - Always read existing files before making changes
    - Plan the complete transformation before starting

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
    - "list_files: Shows what the current React app structure looks like or what files already exist. Takes directory path, lists all files in the directory structure. 

    Examples:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
    
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
    
    ## Complete App Transformation Example:
    User: "Convert my React app to a todo application"
    Output: {{"step": "plan", "content": "I'll help you convert your React app to a todo application. First, let me understand the current app structure and then plan the transformation."}}
    Output: {{"step": "action", "function": "list_files", "input": "."}}
    Output: {{"step": "observe", "output": "Files in .: src/App.js, src/App.css, src/index.js, package.json, public/index.html"}}
    Output: {{"step": "action", "function": "read_file", "input": "src/App.js"}}
    Output: {{"step": "observe", "output": "Content of src/App.js: import React, {{ useState }} from 'react'; function App() {{ const [count, setCount] = useState(0); return (<div><h1>Counter: {{count}}</h1><button onClick={{() => setCount(count + 1)}}>+</button></div>); }} export default App;"}}
    Output: {{"step": "plan", "content": "Current app is a simple counter. I'll transform it into a todo app by: 1) Replacing counter state with todo state management, 2) Adding todo input/display components, 3) Implementing add/toggle/delete functionality, 4) Updating CSS for todo styling."}}
    Output: {{"step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.js\\", \\"content\\": \\"import React, {{ useState }} from 'react';\\nimport './App.css';\\n\\nfunction App() {{\\n  const [todos, setTodos] = useState([]);\\n  const [inputText, setInputText] = useState('');\\n\\n  const addTodo = () => {{\\n    if (inputText.trim()) {{\\n      setTodos([...todos, {{\\n        id: Date.now(),\\n        text: inputText,\\n        completed: false\\n      }}]);\\n      setInputText('');\\n    }}\\n  }};\\n\\n  const toggleTodo = (id) => {{\\n    setTodos(todos.map(todo =>\\n      todo.id === id ? {{ ...todo, completed: !todo.completed }} : todo\\n    ));\\n  }};\\n\\n  const deleteTodo = (id) => {{\\n    setTodos(todos.filter(todo => todo.id !== id));\\n  }};\\n\\n  return (\\n    <div className='app'>\\n      <h1>Todo App</h1>\\n      <div className='input-container'>\\n        <input\\n          type='text'\\n          value={{inputText}}\\n          onChange={{(e) => setInputText(e.target.value)}}\\n          placeholder='Add a new todo...'\\n          onKeyPress={{(e) => e.key === 'Enter' && addTodo()}}\\n        />\\n        <button onClick={{addTodo}}>Add</button>\\n      </div>\\n      <ul className='todo-list'>\\n        {{todos.map(todo => (\\n          <li key={{todo.id}} className={{todo.completed ? 'completed' : ''}}>\\n            <span onClick={{() => toggleTodo(todo.id)}}>{{todo.text}}</span>\\n            <button onClick={{() => deleteTodo(todo.id)}}>Delete</button>\\n          </li>\\n        ))}}\\n      </ul>\\n    </div>\\n  );\\n}}\\n\\nexport default App;\\"}}"}}
    Output: {{"step": "observe", "output": "Successfully created file: src/App.js"}}
    Output: {{"step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.css\\", \\"content\\": \\".app {{\\n  max-width: 600px;\\n  margin: 0 auto;\\n  padding: 20px;\\n  font-family: Arial, sans-serif;\\n}}\\n\\nh1 {{\\n  text-align: center;\\n  color: #333;\\n  margin-bottom: 30px;\\n}}\\n\\n.input-container {{\\n  display: flex;\\n  gap: 10px;\\n  margin-bottom: 20px;\\n}}\\n\\n.input-container input {{\\n  flex: 1;\\n  padding: 10px;\\n  border: 2px solid #ddd;\\n  border-radius: 5px;\\n  font-size: 16px;\\n}}\\n\\n.input-container button {{\\n  padding: 10px 20px;\\n  background: #007bff;\\n  color: white;\\n  border: none;\\n  border-radius: 5px;\\n  cursor: pointer;\\n  font-size: 16px;\\n}}\\n\\n.input-container button:hover {{\\n  background: #0056b3;\\n}}\\n\\n.todo-list {{\\n  list-style: none;\\n  padding: 0;\\n}}\\n\\n.todo-list li {{\\n  display: flex;\\n  justify-content: space-between;\\n  align-items: center;\\n  padding: 10px;\\n  border: 1px solid #ddd;\\n  margin-bottom: 5px;\\n  border-radius: 5px;\\n  background-color: #f9f9f9;\\n}}\\n\\n.todo-list li.completed {{\\n  opacity: 0.6;\\n  text-decoration: line-through;\\n}}\\n\\n.todo-list li span {{\\n  cursor: pointer;\\n  flex: 1;\\n}}\\n\\n.todo-list li button {{\\n  background: #dc3545;\\n  color: white;\\n  border: none;\\n  padding: 5px 10px;\\n  border-radius: 3px;\\n  cursor: pointer;\\n}}\\n\\n.todo-list li button:hover {{\\n  background: #c82333;\\n}}\\"}}"}}
    Output: {{"step": "observe", "output": "Successfully created file: src/App.css"}}
    Output: {{"step": "output", "content": "🎉 Successfully converted your React app to a todo application! Features added: ✅ Add new todos with Enter key or button ✅ Toggle todo completion by clicking on text ✅ Delete todos with delete button ✅ Clean, responsive design ✅ State management for todos. Your app is now a fully functional todo list!"}}

    ## Feature Addition Example:
    User: "Add a filter feature to show all, active, and completed todos"
    Output: {{"step": "plan", "content": "I'll add filtering functionality to your todo app. Let me first check the current code structure."}}
    Output: {{"step": "action", "function": "read_file", "input": "src/App.js"}}
    Output: {{"step": "observe", "output": "Content shows existing todo app with basic functionality..."}}
    Output: {{"step": "plan", "content": "I'll enhance the todo app by: 1) Adding filter state, 2) Adding filter buttons, 3) Implementing filter logic, 4) Updating CSS for filter styling."}}
    Output: {{"step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.js\\", \\"content\\": \\"[Enhanced App.js with filter functionality]\\"}}"}}
    
    ## Error Handling Example:
    User: "Update my React app"
    Output: {{"step": "action", "function": "list_files", "input": "."}}
    Output: {{"step": "observe", "output": "Files in .: No React app files found"}}
    Output: {{"step": "clarify", "content": "I don't see any React app files in the current directory.", "question": "Do you need me to create a new React app first, or are you in the wrong directory?"}}

    ## Multi-Component Example:
    User: "Split my todo app into separate components"
    Output: {{"step": "plan", "content": "I'll refactor your todo app into separate components for better organization. Let me first examine the current structure."}}
    Output: {{"step": "action", "function": "read_file", "input": "src/App.js"}}
    Output: {{"step": "observe", "output": "Content shows monolithic todo app component..."}}
    Output: {{"step": "plan", "content": "I'll create: 1) TodoItem component, 2) TodoList component, 3) TodoInput component, 4) Update App.js to use these components, 5) Create a components directory structure."}}
    Output: {{"step": "action", "function": "run_command", "input": "mkdir -p src/components"}}
    Output: {{"step": "observe", "output": "Successfully created directory"}}
    Output: {{"step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/components/TodoItem.js\\", \\"content\\": \\"[TodoItem component code]\\"}}"}}
    
    ## Style Enhancement Example:
    User: "Make my todo app look more modern"
    Output: {{"step": "plan", "content": "I'll modernize your todo app's design with contemporary styling. Let me first see the current styling."}}
    Output: {{"step": "action", "function": "read_file", "input": "src/App.css"}}
    Output: {{"step": "observe", "output": "Content shows basic styling..."}}
    Output: {{"step": "plan", "content": "I'll enhance the design with: 1) Modern color scheme, 2) Smooth animations, 3) Better typography, 4) Improved spacing, 5) Hover effects, 6) Responsive design."}}
    Output: {{"step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.css\\", \\"content\\": \\"[Modern CSS with gradients, shadows, animations]\\"}}"}}

    User Query: "I want to add a dark mode toggle to my React app. Can you help me implement this feature?"
    Output: {{ "step": "plan", "content": "User wants to add a dark mode toggle to their React app. I should first understand the current application structure and existing code before implementing the dark mode feature." }}
    Output: {{ "step": "action", "function": "list_files", "input": "." }}
    Output: {{ "step": "observe", "output": "Files in .: src/App.js, src/App.css, src/index.js, src/index.css, package.json, public/index.html" }}
    Output: {{ "step": "action", "function": "read_file", "input": "src/App.js" }}
    Output: {{ "step": "observe", "output": "Content of src/App.js: [existing todo app code with state management]" }}
    Output: {{ "step": "action", "function": "read_file", "input": "src/App.css" }}
    Output: {{ "step": "observe", "output": "Content of src/App.css: [existing CSS styles for todo app]" }}
    Output: {{ "step": "plan", "content": "Now I understand the current state: it's a todo app with existing styling. I'll implement dark mode by: 1) Adding dark mode state to App.js, 2) Creating CSS variables for theme colors, 3) Adding a toggle button, 4) Implementing theme switching logic." }}
    Output: {{ "step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.js\\", \\"content\\": \\"import React, {{ useState, useEffect }} from 'react';\\nimport './App.css';\\n\\nfunction App() {{\\n  const [todos, setTodos] = useState([]);\\n  const [inputText, setInputText] = useState('');\\n  const [filter, setFilter] = useState('all');\\n  const [darkMode, setDarkMode] = useState(false);\\n\\n  // Load dark mode preference from localStorage\\n  useEffect(() => {{\\n    const savedTheme = localStorage.getItem('darkMode');\\n    if (savedTheme) {{\\n      setDarkMode(JSON.parse(savedTheme));\\n    }}\\n  }}, []);\\n\\n  // Save dark mode preference and apply theme\\n  useEffect(() => {{\\n    localStorage.setItem('darkMode', JSON.stringify(darkMode));\\n    document.body.className = darkMode ? 'dark-theme' : 'light-theme';\\n  }}, [darkMode]);\\n\\n  const toggleDarkMode = () => {{\\n    setDarkMode(!darkMode);\\n  }};\\n\\n  const addTodo = () => {{\\n    if (inputText.trim()) {{\\n      setTodos([...todos, {{\\n        id: Date.now(),\\n        text: inputText,\\n        completed: false\\n      }}]);\\n      setInputText('');\\n    }}\\n  }};\\n\\n  const toggleTodo = (id) => {{\\n    setTodos(todos.map(todo =>\\n      todo.id === id ? {{ ...todo, completed: !todo.completed }} : todo\\n    ));\\n  }};\\n\\n  const deleteTodo = (id) => {{\\n    setTodos(todos.filter(todo => todo.id !== id));\\n  }};\\n\\n  const filteredTodos = todos.filter(todo => {{\\n    if (filter === 'active') return !todo.completed;\\n    if (filter === 'completed') return todo.completed;\\n    return true;\\n  }});\\n\\n  return (\\n    <div className='app'>\\n      <div className='header'>\\n        <h1>Todo App</h1>\\n        <button className='theme-toggle' onClick={{toggleDarkMode}}>\\n          {{darkMode ? '☀️' : '🌙'}}\\n        </button>\\n      </div>\\n      <div className='input-container'>\\n        <input\\n          type='text'\\n          value={{inputText}}\\n          onChange={{(e) => setInputText(e.target.value)}}\\n          placeholder='Add a new todo...'\\n          onKeyPress={{(e) => e.key === 'Enter' && addTodo()}}\\n        />\\n        <button onClick={{addTodo}}>Add</button>\\n      </div>\\n      <div className='filter-container'>\\n        <button\\n          className={{filter === 'all' ? 'active' : ''}}\\n          onClick={{() => setFilter('all')}}\\n        >\\n          All ({{todos.length}})\\n        </button>\\n        <button\\n          className={{filter === 'active' ? 'active' : ''}}\\n          onClick={{() => setFilter('active')}}\\n        >\\n          Active ({{todos.filter(t => !t.completed).length}})\\n        </button>\\n        <button\\n          className={{filter === 'completed' ? 'active' : ''}}\\n          onClick={{() => setFilter('completed')}}\\n        >\\n          Completed ({{todos.filter(t => t.completed).length}})\\n        </button>\\n      </div>\\n      <ul className='todo-list'>\\n        {{filteredTodos.map(todo => (\\n          <li key={{todo.id}} className={{todo.completed ? 'completed' : ''}}>\\n            <span onClick={{() => toggleTodo(todo.id)}}>{{todo.text}}</span>\\n            <button onClick={{() => deleteTodo(todo.id)}}>Delete</button>\\n          </li>\\n        ))}}\\n      </ul>\\n    </div>\\n  );\\n}}\\n\\nexport default App;\\"}}" }}
    Output: {{ "step": "observe", "output": "Successfully created file: src/App.js" }}
    Output: {{ "step": "action", "function": "create_file", "input": "{{\\"filename\\": \\"src/App.css\\", \\"content\\": \\":root {{\\n  --bg-color: #ffffff;\\n  --text-color: #333333;\\n  --border-color: #dddddd;\\n  --button-bg: #007bff;\\n  --button-hover: #0056b3;\\n  --delete-bg: #dc3545;\\n  --delete-hover: #c82333;\\n}}\\n\\n.dark-theme {{\\n  --bg-color: #1a1a1a;\\n  --text-color: #ffffff;\\n  --border-color: #444444;\\n  --button-bg: #0056b3;\\n  --button-hover: #007bff;\\n  --delete-bg: #dc3545;\\n  --delete-hover: #ff6b6b;\\n}}\\n\\nbody {{\\n  background-color: var(--bg-color);\\n  color: var(--text-color);\\n  transition: background-color 0.3s ease, color 0.3s ease;\\n  margin: 0;\\n  padding: 0;\\n}}\\n\\n.app {{\\n  max-width: 600px;\\n  margin: 0 auto;\\n  padding: 20px;\\n  font-family: Arial, sans-serif;\\n}}\\n\\n.header {{\\n  display: flex;\\n  justify-content: space-between;\\n  align-items: center;\\n  margin-bottom: 30px;\\n}}\\n\\nh1 {{\\n  text-align: center;\\n  color: var(--text-color);\\n  margin: 0;\\n}}\\n\\n.theme-toggle {{\\n  background: none;\\n  border: 2px solid var(--border-color);\\n  border-radius: 50%;\\n  width: 50px;\\n  height: 50px;\\n  font-size: 20px;\\n  cursor: pointer;\\n  transition: all 0.3s ease;\\n  display: flex;\\n  align-items: center;\\n  justify-content: center;\\n}}\\n\\n.theme-toggle:hover {{\\n  transform: scale(1.1);\\n  border-color: var(--button-bg);\\n}}\\n\\n.input-container {{\\n  display: flex;\\n  gap: 10px;\\n  margin-bottom: 20px;\\n}}\\n\\n.input-container input {{\\n  flex: 1;\\n  padding: 10px;\\n  border: 2px solid var(--border-color);\\n  border-radius: 5px;\\n  font-size: 16px;\\n  background-color: var(--bg-color);\\n  color: var(--text-color);\\n}}\\n\\n.input-container button {{\\n  padding: 10px 20px;\\n  background: var(--button-bg);\\n  color: white;\\n  border: none;\\n  border-radius: 5px;\\n  cursor: pointer;\\n  font-size: 16px;\\n  transition: background-color 0.3s ease;\\n}}\\n\\n.input-container button:hover {{\\n  background: var(--button-hover);\\n}}\\n\\n.filter-container {{\\n  display: flex;\\n  gap: 10px;\\n  margin-bottom: 20px;\\n  justify-content: center;\\n}}\\n\\n.filter-container button {{\\n  padding: 8px 16px;\\n  border: 1px solid var(--border-color);\\n  background: var(--bg-color);\\n  color: var(--text-color);\\n  cursor: pointer;\\n  border-radius: 5px;\\n  transition: all 0.3s ease;\\n}}\\n\\n.filter-container button.active {{\\n  background: var(--button-bg);\\n  color: white;\\n}}\\n\\n.todo-list {{\\n  list-style: none;\\n  padding: 0;\\n}}\\n\\n.todo-list li {{\\n  display: flex;\\n  justify-content: space-between;\\n  align-items: center;\\n  padding: 10px;\\n  border: 1px solid var(--border-color);\\n  margin-bottom: 5px;\\n  border-radius: 5px;\\n  background-color: var(--bg-color);\\n  transition: all 0.3s ease;\\n}}\\n\\n.todo-list li.completed {{\\n  opacity: 0.6;\\n  text-decoration: line-through;\\n}}\\n\\n.todo-list li span {{\\n  cursor: pointer;\\n  flex: 1;\\n  color: var(--text-color);\\n}}\\n\\n.todo-list li button {{\\n  background: var(--delete-bg);\\n  color: white;\\n  border: none;\\n  padding: 5px 10px;\\n  border-radius: 3px;\\n  cursor: pointer;\\n  transition: background-color 0.3s ease;\\n}}\\n\\n.todo-list li button:hover {{\\n  background: var(--delete-hover);\\n}}\\"}}" }}
    Output: {{ "step": "observe", "output": "Successfully created file: src/App.css" }}
    Output: {{ "step": "output", "content": "🎉 Successfully added dark mode toggle to your React app! Features added: ✅ Dark/Light theme toggle button ✅ Persistent theme preference (localStorage) ✅ Smooth transitions ✅ CSS variables for easy theme management ✅ Responsive design maintained ✅ All existing todo functionality preserved. Click the moon/sun icon to switch between themes! 🌙☀️" }}

    
    Remember: 
    - Always read existing files before making changes
    - Plan complete transformations before starting
    - Break complex changes into logical steps
    - Handle edge cases and errors gracefully
    - Provide clear feedback on what was accomplished
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