import subprocess
import os
import sys
import psutil
import winreg
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import win32process
import win32security
import win32service
import win32serviceutil
import wmi
import platform
import socket
import requests
import json
from datetime import datetime
import threading
import time

class SystemController:
    def __init__(self):
        self.wmi_connection = wmi.WMI()
        self.is_admin = self.check_admin_privileges()
        
    def check_admin_privileges(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def request_admin_privileges(self):
        """Request administrator privileges"""
        if not self.is_admin:
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return True
            except:
                return False
        return True
    
    # PROCESS MANAGEMENT
    def list_processes(self):
        """List all running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def kill_process(self, process_name_or_pid):
        """Kill a process by name or PID"""
        try:
            if isinstance(process_name_or_pid, int):
                # Kill by PID
                proc = psutil.Process(process_name_or_pid)
                proc.terminate()
                return f"Process {process_name_or_pid} terminated"
            else:
                # Kill by name
                killed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    if process_name_or_pid.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed_count += 1
                return f"Terminated {killed_count} processes matching '{process_name_or_pid}'"
        except Exception as e:
            return f"Error killing process: {e}"
    
    def start_process(self, executable_path, args=""):
        """Start a new process"""
        try:
            if args:
                subprocess.Popen(f"{executable_path} {args}", shell=True)
            else:
                subprocess.Popen(executable_path, shell=True)
            return f"Started process: {executable_path}"
        except Exception as e:
            return f"Error starting process: {e}"
    
    # SYSTEM INFORMATION
    def get_system_info(self):
        """Get comprehensive system information"""
        info = {
            "OS": platform.system() + " " + platform.release(),
            "Architecture": platform.architecture()[0],
            "Processor": platform.processor(),
            "Machine": platform.machine(),
            "Node": platform.node(),
            "CPU_Count": psutil.cpu_count(),
            "CPU_Usage": psutil.cpu_percent(interval=1),
            "Memory": {
                "Total": psutil.virtual_memory().total,
                "Available": psutil.virtual_memory().available,
                "Used": psutil.virtual_memory().used,
                "Percentage": psutil.virtual_memory().percent
            },
            "Disk": []
        }
        
        # Disk information
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info["Disk"].append({
                    "Device": partition.device,
                    "Mountpoint": partition.mountpoint,
                    "File_system": partition.fstype,
                    "Total": usage.total,
                    "Used": usage.used,
                    "Free": usage.free,
                    "Percentage": (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
        
        return info
    
    def get_network_info(self):
        """Get network information"""
        info = {
            "Hostname": socket.gethostname(),
            "IP_Address": socket.gethostbyname(socket.gethostname()),
            "Network_Interfaces": []
        }
        
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {"Interface": interface, "Addresses": []}
            for addr in addrs:
                interface_info["Addresses"].append({
                    "Family": str(addr.family),
                    "Address": addr.address,
                    "Netmask": addr.netmask,
                    "Broadcast": addr.broadcast
                })
            info["Network_Interfaces"].append(interface_info)
        
        return info
    
    # FILE SYSTEM OPERATIONS
    def create_file(self, filepath, content=""):
        """Create a file with optional content"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File created: {filepath}"
        except Exception as e:
            return f"Error creating file: {e}"
    
    def delete_file(self, filepath):
        """Delete a file"""
        try:
            os.remove(filepath)
            return f"File deleted: {filepath}"
        except Exception as e:
            return f"Error deleting file: {e}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            import shutil
            shutil.copy2(source, destination)
            return f"File copied from {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {e}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            import shutil
            shutil.move(source, destination)
            return f"File moved from {source} to {destination}"
        except Exception as e:
            return f"Error moving file: {e}"
    
    def list_directory(self, directory_path):
        """List directory contents"""
        try:
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else 0
                modified = datetime.fromtimestamp(os.path.getmtime(item_path))
                items.append({
                    "Name": item,
                    "Type": "Directory" if is_dir else "File",
                    "Size": size,
                    "Modified": modified.strftime("%Y-%m-%d %H:%M:%S")
                })
            return items
        except Exception as e:
            return f"Error listing directory: {e}"
    
    # REGISTRY OPERATIONS
    def read_registry(self, key_path, value_name):
        """Read Windows registry value"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except Exception as e:
            return f"Error reading registry: {e}"
    
    def write_registry(self, key_path, value_name, value, value_type=winreg.REG_SZ):
        """Write Windows registry value"""
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return f"Registry value set: {key_path}\\{value_name} = {value}"
        except Exception as e:
            return f"Error writing registry: {e}"
    
    # SERVICE MANAGEMENT
    def list_services(self):
        """List Windows services"""
        try:
            services = []
            for service in self.wmi_connection.Win32_Service():
                services.append({
                    "Name": service.Name,
                    "DisplayName": service.DisplayName,
                    "State": service.State,
                    "StartMode": service.StartMode,
                    "ProcessId": service.ProcessId
                })
            return services
        except Exception as e:
            return f"Error listing services: {e}"
    
    def start_service(self, service_name):
        """Start a Windows service"""
        try:
            win32serviceutil.StartService(service_name)
            return f"Service started: {service_name}"
        except Exception as e:
            return f"Error starting service: {e}"
    
    def stop_service(self, service_name):
        """Stop a Windows service"""
        try:
            win32serviceutil.StopService(service_name)
            return f"Service stopped: {service_name}"
        except Exception as e:
            return f"Error stopping service: {e}"
    
    # HARDWARE CONTROL
    def get_hardware_info(self):
        """Get hardware information"""
        try:
            hardware_info = {
                "CPU": [],
                "Memory": [],
                "Disk": [],
                "Network": [],
                "Graphics": []
            }
            
            # CPU Information
            for cpu in self.wmi_connection.Win32_Processor():
                hardware_info["CPU"].append({
                    "Name": cpu.Name,
                    "Manufacturer": cpu.Manufacturer,
                    "MaxClockSpeed": cpu.MaxClockSpeed,
                    "NumberOfCores": cpu.NumberOfCores,
                    "NumberOfLogicalProcessors": cpu.NumberOfLogicalProcessors
                })
            
            # Memory Information
            for memory in self.wmi_connection.Win32_PhysicalMemory():
                hardware_info["Memory"].append({
                    "Capacity": memory.Capacity,
                    "Speed": memory.Speed,
                    "Manufacturer": memory.Manufacturer,
                    "PartNumber": memory.PartNumber
                })
            
            # Disk Information
            for disk in self.wmi_connection.Win32_DiskDrive():
                hardware_info["Disk"].append({
                    "Model": disk.Model,
                    "Size": disk.Size,
                    "InterfaceType": disk.InterfaceType,
                    "MediaType": disk.MediaType
                })
            
            # Network Adapters
            for adapter in self.wmi_connection.Win32_NetworkAdapter():
                if adapter.NetConnectionStatus:
                    hardware_info["Network"].append({
                        "Name": adapter.Name,
                        "MACAddress": adapter.MACAddress,
                        "AdapterType": adapter.AdapterType,
                        "Speed": adapter.Speed
                    })
            
            # Graphics Cards
            for gpu in self.wmi_connection.Win32_VideoController():
                hardware_info["Graphics"].append({
                    "Name": gpu.Name,
                    "AdapterRAM": gpu.AdapterRAM,
                    "DriverVersion": gpu.DriverVersion,
                    "VideoProcessor": gpu.VideoProcessor
                })
            
            return hardware_info
        except Exception as e:
            return f"Error getting hardware info: {e}"
    
    # POWER MANAGEMENT
    def shutdown_system(self, delay=0):
        """Shutdown the system"""
        try:
            subprocess.run(f"shutdown /s /t {delay}", shell=True)
            return f"System shutdown initiated (delay: {delay} seconds)"
        except Exception as e:
            return f"Error shutting down system: {e}"
    
    def restart_system(self, delay=0):
        """Restart the system"""
        try:
            subprocess.run(f"shutdown /r /t {delay}", shell=True)
            return f"System restart initiated (delay: {delay} seconds)"
        except Exception as e:
            return f"Error restarting system: {e}"
    
    def hibernate_system(self):
        """Hibernate the system"""
        try:
            subprocess.run("shutdown /h", shell=True)
            return "System hibernation initiated"
        except Exception as e:
            return f"Error hibernating system: {e}"
    
    def sleep_system(self):
        """Put system to sleep"""
        try:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return "System sleep initiated"
        except Exception as e:
            return f"Error putting system to sleep: {e}"
    
    # NETWORK OPERATIONS
    def ping_host(self, hostname):
        """Ping a host"""
        try:
            result = subprocess.run(f"ping -n 4 {hostname}", shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error pinging host: {e}"
    
    def get_public_ip(self):
        """Get public IP address"""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            return response.json()["ip"]
        except Exception as e:
            return f"Error getting public IP: {e}"
    
    # ADVANCED SYSTEM CONTROL
    def execute_command(self, command):
        """Execute any system command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error executing command: {e}"
    
    def schedule_task(self, task_name, command, schedule_time):
        """Schedule a task using Windows Task Scheduler"""
        try:
            schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{command}" /sc once /st {schedule_time}'
            result = subprocess.run(schtasks_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Task '{task_name}' scheduled successfully"
            else:
                return f"Error scheduling task: {result.stderr}"
        except Exception as e:
            return f"Error scheduling task: {e}"
    
    def get_installed_programs(self):
        """Get list of installed programs"""
        try:
            programs = []
            for program in self.wmi_connection.Win32_Product():
                programs.append({
                    "Name": program.Name,
                    "Version": program.Version,
                    "Vendor": program.Vendor,
                    "InstallDate": program.InstallDate
                })
            return programs
        except Exception as e:
            return f"Error getting installed programs: {e}"
    
    def monitor_system_resources(self, duration=10):
        """Monitor system resources for specified duration"""
        try:
            monitoring_data = []
            for i in range(duration):
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": psutil.disk_io_counters()._asdict(),
                    "network_io": psutil.net_io_counters()._asdict()
                }
                monitoring_data.append(data)
                time.sleep(1)
            return monitoring_data
        except Exception as e:
            return f"Error monitoring system: {e}"

# Global system controller instance
system_controller = SystemController()