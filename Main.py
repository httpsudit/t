from Frontend.GUI import GraphicalUserInterface
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.VoiceRecognition import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.FaceAuthentication import authenticate_user
from Backend.Utils import AnswerModifier, QueryModifier
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import queue
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f"""{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?"""

functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
subprocess_list = []

# Global queues for inter-thread communication
gui_update_queue = queue.Queue()
mic_status_queue = queue.Queue()

def ShowDefaultChatIfNoChats():
    """Ensure a default chat log exists if no chats are logged"""
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                gui_update_queue.put(('chat', DefaultMessage))
    except FileNotFoundError:
        print("ChatLog.json file not found. Creating default response.")
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        gui_update_queue.put(('chat', DefaultMessage))

def ReadChatLogJson():
    """Read chat log from JSON"""
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        print("ChatLog.json not found.")
        return []

def ChatLogIntegration():
    """Integrate chat logs into a readable format"""
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

    if formatted_chatlog:
        gui_update_queue.put(('chat', AnswerModifier(formatted_chatlog)))

def InitialExecution():
    """Initial execution setup"""
    print("Initializing JARVIS...")
    gui_update_queue.put(('status', "Initializing..."))
    
    # Ensure Data directory exists
    os.makedirs("Data", exist_ok=True)
    os.makedirs("Data/Faces", exist_ok=True)
    
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    
    gui_update_queue.put(('status', "Ready to assist..."))
    print("JARVIS initialized successfully!")

def MainExecution():
    """Main execution logic"""
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        gui_update_queue.put(('status', "Listening..."))
        Query = SpeechRecognition(gui_update_queue)
        
        if not Query:
            return False
            
        gui_update_queue.put(('chat', f"{Username}: {Query}"))
        gui_update_queue.put(('status', "Thinking..."))
        
        Decision = FirstLayerDMM(Query)
        print(f"\nDecision: {Decision}\n")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Merged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )

        # Check for image generation
        for queries in Decision:
            if "generate" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        # Check for automation tasks
        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in functions):
                    gui_update_queue.put(('status', "Executing commands..."))
                    run(Automation(list(Decision)))
                    TaskExecution = True

        # Handle image generation
        if ImageExecution:
            gui_update_queue.put(('status', "Generating images..."))
            with open(r'Frontend\Files\ImageGeneration.data', "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:
                p1 = subprocess.Popen(
                    ['python', r"Backend\ImageGeneration.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocess_list.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        # Handle queries
        if G and R or R:
            gui_update_queue.put(('status', "Searching..."))
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            gui_update_queue.put(('chat', f"{Assistantname}: {Answer}"))
            gui_update_queue.put(('status', "Speaking..."))
            TextToSpeech(Answer)
            return True
        else:
            for queries in Decision:
                if "general" in queries:
                    gui_update_queue.put(('status', "Thinking..."))
                    QueryFinal = queries.replace("general", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    gui_update_queue.put(('chat', f"{Assistantname}: {Answer}"))
                    gui_update_queue.put(('status', "Speaking..."))
                    TextToSpeech(Answer)
                    return True
                elif "realtime" in queries:
                    gui_update_queue.put(('status', "Searching..."))
                    QueryFinal = queries.replace("realtime", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    gui_update_queue.put(('chat', f"{Assistantname}: {Answer}"))
                    gui_update_queue.put(('status', "Speaking..."))
                    TextToSpeech(Answer)
                    return True
                elif "exit" in queries:
                    QueryFinal = "Goodbye! It was nice talking to you."
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    gui_update_queue.put(('chat', f"{Assistantname}: {Answer}"))
                    gui_update_queue.put(('status', "Goodbye..."))
                    TextToSpeech(Answer)
                    sys.exit(0)
                    
    except Exception as e:
        print(f"Error in MainExecution: {e}")
        gui_update_queue.put(('status', "Error occurred"))
        return False

def FirstThread():
    """Thread for primary execution loop"""
    mic_listening = False
    
    while True:
        try:
            # Check microphone status from GUI
            try:
                mic_status = mic_status_queue.get_nowait()
                mic_listening = mic_status
                print(f"Microphone status changed: {mic_listening}")
            except queue.Empty:
                pass

            if mic_listening:
                print("Executing MainExecution")
                MainExecution()
                mic_listening = False  # Reset after processing
            else:
                gui_update_queue.put(('status', "Ready to assist..."))
                sleep(0.1)
                
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            sleep(1)

def SecondThread():
    """Thread for GUI execution"""
    try:
        GraphicalUserInterface(gui_update_queue, mic_status_queue)
    except Exception as e:
        print(f"Error in SecondThread: {e}")

def AuthenticationThread():
    """Thread for face authentication"""
    print("Starting face authentication...")
    gui_update_queue.put(('status', "Authenticating..."))
    
    # For now, we'll skip actual face authentication and proceed
    # In production, uncomment the line below:
    # success = authenticate_user()
    success = True  # Skip authentication for testing
    
    if success:
        print("Authentication successful!")
        gui_update_queue.put(('status', "Authentication successful!"))
        return True
    else:
        print("Authentication failed!")
        gui_update_queue.put(('status', "Authentication failed!"))
        sys.exit(1)

if __name__ == "__main__":
    print("Starting JARVIS AI Assistant...")
    
    # Initialize
    InitialExecution()
    
    # Start authentication (in background for now)
    auth_thread = threading.Thread(target=AuthenticationThread, daemon=True)
    auth_thread.start()
    
    # Start main execution thread
    main_thread = threading.Thread(target=FirstThread, daemon=True)
    main_thread.start()
    
    # Start GUI (main thread)
    SecondThread()