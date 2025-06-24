from Backend.SystemController import system_controller
from Backend.NaturalLanguageProcessor import nlp_processor
from Backend.Automation import Automation as BasicAutomation
import asyncio
import json
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")

class AdvancedAutomation:
    def __init__(self):
        self.system_controller = system_controller
        self.nlp_processor = nlp_processor
        self.command_history = []
        
    async def process_natural_command(self, user_input):
        """Process natural language command and execute appropriate system function"""
        try:
            # Log command
            self.command_history.append({
                "timestamp": str(asyncio.get_event_loop().time()),
                "command": user_input,
                "user": Username
            })
            
            # Process with NLP
            parsed_command = self.nlp_processor.process_command(user_input)
            
            if parsed_command["confidence"] < 0.3:
                return "I'm not sure what you want me to do. Could you please rephrase that?"
            
            action = parsed_command["action"]
            parameters = parsed_command["parameters"]
            
            # Execute the appropriate system function
            result = await self.execute_system_function(action, parameters)
            
            return f"Command executed: {parsed_command['interpretation']}\nResult: {result}"
            
        except Exception as e:
            return f"Error processing command: {e}"
    
    async def execute_system_function(self, action, parameters):
        """Execute system function based on action and parameters"""
        try:
            if action == "kill_process":
                return await asyncio.to_thread(
                    self.system_controller.kill_process,
                    parameters.get("process_name", "")
                )
            
            elif action == "start_process":
                return await asyncio.to_thread(
                    self.system_controller.start_process,
                    parameters.get("executable_path", ""),
                    parameters.get("args", "")
                )
            
            elif action == "list_processes":
                processes = await asyncio.to_thread(self.system_controller.list_processes)
                return f"Found {len(processes)} running processes"
            
            elif action == "system_info":
                info = await asyncio.to_thread(self.system_controller.get_system_info)
                return self.format_system_info(info)
            
            elif action == "network_info":
                info = await asyncio.to_thread(self.system_controller.get_network_info)
                return f"Hostname: {info['Hostname']}, IP: {info['IP_Address']}"
            
            elif action == "create_file":
                return await asyncio.to_thread(
                    self.system_controller.create_file,
                    parameters.get("filepath", "untitled.txt"),
                    parameters.get("content", "")
                )
            
            elif action == "delete_file":
                return await asyncio.to_thread(
                    self.system_controller.delete_file,
                    parameters.get("filepath", "")
                )
            
            elif action == "copy_file":
                return await asyncio.to_thread(
                    self.system_controller.copy_file,
                    parameters.get("source", ""),
                    parameters.get("destination", "")
                )
            
            elif action == "move_file":
                return await asyncio.to_thread(
                    self.system_controller.move_file,
                    parameters.get("source", ""),
                    parameters.get("destination", "")
                )
            
            elif action == "list_directory":
                items = await asyncio.to_thread(
                    self.system_controller.list_directory,
                    parameters.get("directory_path", ".")
                )
                return f"Directory contains {len(items)} items"
            
            elif action == "shutdown":
                return await asyncio.to_thread(
                    self.system_controller.shutdown_system,
                    parameters.get("delay", 0)
                )
            
            elif action == "restart":
                return await asyncio.to_thread(
                    self.system_controller.restart_system,
                    parameters.get("delay", 0)
                )
            
            elif action == "hibernate":
                return await asyncio.to_thread(self.system_controller.hibernate_system)
            
            elif action == "sleep":
                return await asyncio.to_thread(self.system_controller.sleep_system)
            
            elif action == "ping":
                return await asyncio.to_thread(
                    self.system_controller.ping_host,
                    parameters.get("hostname", "google.com")
                )
            
            elif action == "public_ip":
                return await asyncio.to_thread(self.system_controller.get_public_ip)
            
            elif action == "execute_command":
                result = await asyncio.to_thread(
                    self.system_controller.execute_command,
                    parameters.get("command", "")
                )
                if isinstance(result, dict):
                    return f"Command output:\n{result['stdout']}\nErrors: {result['stderr']}"
                return str(result)
            
            elif action == "schedule_task":
                return await asyncio.to_thread(
                    self.system_controller.schedule_task,
                    parameters.get("task_name", "JARVIS_Task"),
                    parameters.get("command", ""),
                    parameters.get("schedule_time", "12:00")
                )
            
            elif action == "installed_programs":
                programs = await asyncio.to_thread(self.system_controller.get_installed_programs)
                return f"Found {len(programs)} installed programs"
            
            elif action == "monitor_resources":
                data = await asyncio.to_thread(
                    self.system_controller.monitor_system_resources,
                    parameters.get("duration", 10)
                )
                return f"System monitoring completed for {len(data)} seconds"
            
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Error executing {action}: {e}"
    
    def format_system_info(self, info):
        """Format system information for display"""
        if isinstance(info, dict):
            formatted = f"System: {info.get('OS', 'Unknown')}\n"
            formatted += f"Processor: {info.get('Processor', 'Unknown')}\n"
            formatted += f"CPU Usage: {info.get('CPU_Usage', 0)}%\n"
            formatted += f"Memory Usage: {info.get('Memory', {}).get('Percentage', 0)}%\n"
            return formatted
        return str(info)
    
    async def execute_combined_commands(self, commands_list):
        """Execute multiple commands in sequence"""
        results = []
        for command in commands_list:
            if isinstance(command, str):
                # Natural language command
                result = await self.process_natural_command(command)
            else:
                # Structured command
                result = await self.execute_system_function(
                    command.get("action", ""),
                    command.get("parameters", {})
                )
            results.append(result)
        return results
    
    def get_command_history(self):
        """Get command execution history"""
        return self.command_history
    
    def clear_command_history(self):
        """Clear command execution history"""
        self.command_history.clear()
        return "Command history cleared"

# Global advanced automation instance
advanced_automation = AdvancedAutomation()

async def ProcessAdvancedCommand(user_input):
    """Main function to process advanced commands"""
    return await advanced_automation.process_natural_command(user_input)

if __name__ == "__main__":
    # Test advanced automation
    async def test():
        commands = [
            "Show me system information",
            "Kill Chrome browser",
            "Create a file called test.txt with hello world content",
            "Ping google.com",
            "List all running processes"
        ]
        
        for cmd in commands:
            print(f"\nCommand: {cmd}")
            result = await ProcessAdvancedCommand(cmd)
            print(f"Result: {result}")
    
    asyncio.run(test())