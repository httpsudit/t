from groq import Groq
from dotenv import dotenv_values
import re
import json

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

class NaturalLanguageProcessor:
    def __init__(self):
        self.system_commands = {
            # Process Management
            "kill_process": ["kill", "terminate", "end", "stop", "close"],
            "start_process": ["start", "run", "launch", "execute", "open"],
            "list_processes": ["list processes", "show processes", "running processes"],
            
            # System Information
            "system_info": ["system info", "system information", "computer specs", "hardware info"],
            "network_info": ["network info", "ip address", "network status"],
            
            # File Operations
            "create_file": ["create file", "make file", "new file"],
            "delete_file": ["delete file", "remove file", "erase file"],
            "copy_file": ["copy file", "duplicate file"],
            "move_file": ["move file", "relocate file"],
            "list_directory": ["list files", "show files", "directory contents"],
            
            # System Control
            "shutdown": ["shutdown", "turn off", "power off"],
            "restart": ["restart", "reboot", "reset"],
            "hibernate": ["hibernate", "sleep mode"],
            "sleep": ["sleep", "standby"],
            
            # Network Operations
            "ping": ["ping", "test connection"],
            "public_ip": ["public ip", "external ip", "my ip"],
            
            # Advanced Operations
            "execute_command": ["execute", "run command", "command"],
            "schedule_task": ["schedule", "set reminder", "create task"],
            "installed_programs": ["installed programs", "software list"],
            "monitor_resources": ["monitor system", "system performance", "resource usage"]
        }
        
        self.preamble = """
        You are an advanced Natural Language Processing system for JARVIS AI Assistant.
        Your job is to interpret user commands and convert them into structured system operations.
        
        Analyze the user's natural language input and determine:
        1. The primary action they want to perform
        2. Any parameters or arguments needed
        3. The appropriate system function to call
        
        Return a JSON response with:
        {
            "action": "function_name",
            "parameters": {
                "param1": "value1",
                "param2": "value2"
            },
            "confidence": 0.95,
            "interpretation": "Human readable interpretation"
        }
        
        Available actions:
        - kill_process: Kill a running process
        - start_process: Start a new process/application
        - list_processes: List all running processes
        - system_info: Get system information
        - network_info: Get network information
        - create_file: Create a new file
        - delete_file: Delete a file
        - copy_file: Copy a file
        - move_file: Move a file
        - list_directory: List directory contents
        - shutdown: Shutdown the system
        - restart: Restart the system
        - hibernate: Hibernate the system
        - sleep: Put system to sleep
        - ping: Ping a host
        - public_ip: Get public IP address
        - execute_command: Execute any system command
        - schedule_task: Schedule a task
        - installed_programs: List installed programs
        - monitor_resources: Monitor system resources
        
        Examples:
        User: "Kill Chrome browser"
        Response: {"action": "kill_process", "parameters": {"process_name": "chrome"}, "confidence": 0.9, "interpretation": "Terminate Chrome browser process"}
        
        User: "Show me system information"
        Response: {"action": "system_info", "parameters": {}, "confidence": 0.95, "interpretation": "Display comprehensive system information"}
        
        User: "Create a file called test.txt with hello world content"
        Response: {"action": "create_file", "parameters": {"filepath": "test.txt", "content": "hello world"}, "confidence": 0.9, "interpretation": "Create a new file named test.txt with specified content"}
        """
    
    def process_command(self, user_input):
        """Process natural language command and return structured response"""
        try:
            messages = [
                {"role": "system", "content": self.preamble},
                {"role": "user", "content": user_input}
            ]
            
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=512,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            response = completion.choices[0].message.content
            return json.loads(response)
            
        except Exception as e:
            print(f"Error processing command: {e}")
            return self.fallback_processing(user_input)
    
    def fallback_processing(self, user_input):
        """Fallback processing using pattern matching"""
        user_input_lower = user_input.lower()
        
        # Process management patterns
        if any(word in user_input_lower for word in ["kill", "terminate", "end", "stop"]):
            if "chrome" in user_input_lower:
                return {
                    "action": "kill_process",
                    "parameters": {"process_name": "chrome"},
                    "confidence": 0.8,
                    "interpretation": "Kill Chrome process"
                }
            elif "notepad" in user_input_lower:
                return {
                    "action": "kill_process",
                    "parameters": {"process_name": "notepad"},
                    "confidence": 0.8,
                    "interpretation": "Kill Notepad process"
                }
        
        # System information patterns
        if any(phrase in user_input_lower for phrase in ["system info", "computer specs", "hardware"]):
            return {
                "action": "system_info",
                "parameters": {},
                "confidence": 0.9,
                "interpretation": "Get system information"
            }
        
        # File operations patterns
        if "create file" in user_input_lower or "make file" in user_input_lower:
            # Extract filename
            filename_match = re.search(r'(?:file|called)\s+([^\s]+)', user_input_lower)
            filename = filename_match.group(1) if filename_match else "untitled.txt"
            
            # Extract content
            content_match = re.search(r'(?:with|content)\s+(.+)', user_input_lower)
            content = content_match.group(1) if content_match else ""
            
            return {
                "action": "create_file",
                "parameters": {"filepath": filename, "content": content},
                "confidence": 0.8,
                "interpretation": f"Create file {filename}"
            }
        
        # Power management patterns
        if any(word in user_input_lower for word in ["shutdown", "turn off", "power off"]):
            return {
                "action": "shutdown",
                "parameters": {"delay": 0},
                "confidence": 0.9,
                "interpretation": "Shutdown system"
            }
        
        if any(word in user_input_lower for word in ["restart", "reboot"]):
            return {
                "action": "restart",
                "parameters": {"delay": 0},
                "confidence": 0.9,
                "interpretation": "Restart system"
            }
        
        # Network patterns
        if "ping" in user_input_lower:
            host_match = re.search(r'ping\s+([^\s]+)', user_input_lower)
            host = host_match.group(1) if host_match else "google.com"
            return {
                "action": "ping",
                "parameters": {"hostname": host},
                "confidence": 0.8,
                "interpretation": f"Ping {host}"
            }
        
        # Command execution patterns
        if any(phrase in user_input_lower for phrase in ["run command", "execute", "cmd"]):
            command_match = re.search(r'(?:command|execute|run)\s+(.+)', user_input_lower)
            command = command_match.group(1) if command_match else user_input
            return {
                "action": "execute_command",
                "parameters": {"command": command},
                "confidence": 0.7,
                "interpretation": f"Execute command: {command}"
            }
        
        # Default fallback
        return {
            "action": "execute_command",
            "parameters": {"command": user_input},
            "confidence": 0.5,
            "interpretation": f"Execute as system command: {user_input}"
        }

# Global NLP processor instance
nlp_processor = NaturalLanguageProcessor()