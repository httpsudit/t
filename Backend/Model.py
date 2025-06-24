import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars["CohereAPIKey"]

co = cohere.Client(api_key=CohereAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "advanced_system"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model for JARVIS AI Assistant, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, an 'advanced_system' query, or is asking to perform any task or automation.
*** Do not answer any query, just decide what kind of query is given to you. Your response must be a comma-separated list of commands. ***

**General Queries:**
- Respond with 'general (query)' if a query can be answered by a large language model (LLM) and doesn't require real-time information or system access. Examples:
    - 'who was akbar?' -> 'general who was akbar?'
    - 'how can i study more effectively?' -> 'general how can i study more effectively?'
    - 'can you help me with this math problem?' -> 'general can you help me with this math problem?'
    - 'Thanks, i really liked it.' -> 'general thanks, i really liked it.'
    - 'what is python programming language?' -> 'general what is python programming language?'

**Real-time Queries:**
- Respond with 'realtime (query)' if a query cannot be answered by an LLM alone and requires up-to-date information from the internet. Examples:
    - 'who is indian prime minister' -> 'realtime who is indian prime minister'
    - 'tell me about facebook's recent update.' -> 'realtime tell me about facebook's recent update.'
    - 'tell me news about coronavirus.' -> 'realtime tell me news about coronavirus.'
    - 'what is today's news?' -> 'realtime what is today's news?'

**Advanced System Commands:**
- Respond with 'advanced_system (command)' for any system-level operations, hardware control, software management, or complex system tasks. Examples:
    - 'kill chrome browser' -> 'advanced_system kill chrome browser'
    - 'show system information' -> 'advanced_system show system information'
    - 'create a file called test.txt' -> 'advanced_system create a file called test.txt'
    - 'shutdown the computer' -> 'advanced_system shutdown the computer'
    - 'restart the system' -> 'advanced_system restart the system'
    - 'list all running processes' -> 'advanced_system list all running processes'
    - 'ping google.com' -> 'advanced_system ping google.com'
    - 'delete file example.txt' -> 'advanced_system delete file example.txt'
    - 'copy file from here to there' -> 'advanced_system copy file from here to there'
    - 'run command dir' -> 'advanced_system run command dir'
    - 'execute ipconfig' -> 'advanced_system execute ipconfig'
    - 'terminate notepad' -> 'advanced_system terminate notepad'
    - 'start calculator' -> 'advanced_system start calculator'
    - 'get network information' -> 'advanced_system get network information'
    - 'monitor system performance' -> 'advanced_system monitor system performance'
    - 'schedule a task' -> 'advanced_system schedule a task'
    - 'hibernate the computer' -> 'advanced_system hibernate the computer'
    - 'put system to sleep' -> 'advanced_system put system to sleep'
    - 'show installed programs' -> 'advanced_system show installed programs'
    - 'get hardware information' -> 'advanced_system get hardware information'

**Basic Application/System Commands:**
- **Open Application/Website**: Respond with 'open (application name or website name)'. Examples:
    - 'open facebook' -> 'open facebook'
    - 'open chrome and firefox' -> 'open chrome, open firefox'
- **Close Application**: Respond with 'close (application name)'. Examples:
    - 'close notepad' -> 'close notepad'
- **Play Song**: Respond with 'play (song name)'. Examples:
    - 'play afsanay by ys' -> 'play afsanay by ys'
- **Generate Image**: Respond with 'generate image (image prompt)'. Examples:
    - 'generate image of a lion' -> 'generate image of a lion'
- **Set Reminder**: Respond with 'reminder (datetime with message)'. Example:
    - 'set a reminder at 9:00pm on 25th june for my business meeting.' -> 'reminder 9:00pm 25th june business meeting'
- **System Control**: Respond with 'system (task name)' for basic audio controls like mute, unmute, volume up, volume down. Examples:
    - 'mute the volume' -> 'system mute'
- **Content Writing**: Respond with 'content (topic)' for writing applications, codes, emails, essays, etc. Examples:
    - 'write an application for sick leave' -> 'content application for sick leave'
- **Google Search**: Respond with 'google search (topic)'. Examples:
    - 'google search latest AI news' -> 'google search latest AI news'
- **YouTube Search**: Respond with 'youtube search (topic)'. Examples:
    - 'youtube search python tutorials' -> 'youtube search python tutorials'

**Combined Commands:**
- If the query asks to perform multiple tasks, combine them with commas. Example:
    - 'open facebook, telegram and close whatsapp' -> 'open facebook, open telegram, close whatsapp'
    - 'kill chrome and start notepad' -> 'advanced_system kill chrome, advanced_system start notepad'

**Ending Conversation:**
- If the user is saying goodbye or wants to end the conversation, respond with 'exit'. Example:
    - 'bye jarvis.' -> 'exit'

**Priority Rules:**
1. If a command involves system-level operations, hardware control, process management, file operations, or complex system tasks, always use 'advanced_system'
2. Use 'open', 'close', 'play' etc. only for simple application launching/closing
3. Use 'system' only for basic audio controls (mute, unmute, volume)
4. When in doubt between 'system' and 'advanced_system', choose 'advanced_system'

**Fallback:**
- Respond with 'general (query)' if you cannot decide the type of query or if it asks to perform a task not clearly categorized above.
"""

ChatHistory = [
    {"role": "User", "message": "how are you ?"},
    {"role": "Chatbot", "message": "general how are you ?"},
    {"role": "User", "message": "kill chrome browser"},
    {"role": "Chatbot", "message": "advanced_system kill chrome browser"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "shutdown the computer"},
    {"role": "Chatbot", "message": "advanced_system shutdown the computer"},
    {"role": "User", "message": "create a file called test.txt with hello world"},
    {"role": "Chatbot", "message": "advanced_system create a file called test.txt with hello world"},
    {"role": "User", "message": "show system information"},
    {"role": "Chatbot", "message": "advanced_system show system information"},
    {"role": "User", "message": "run command ipconfig"},
    {"role": "Chatbot", "message": "advanced_system run command ipconfig"},
    {"role": "User", "message": "mute the volume"},
    {"role": "Chatbot", "message": "system mute"},
    {"role": "User", "message": "generate image of a cat and kill notepad"},
    {"role": "Chatbot", "message": "generate image of a cat, advanced_system kill notepad"},
    {"role": "User", "message": "play some music and open youtube"},
    {"role": "Chatbot", "message": "play some music, open youtube"},
    {"role": "User", "message": "terminate all chrome processes and start calculator"},
    {"role": "Chatbot", "message": "advanced_system terminate all chrome processes, advanced_system start calculator"}
]

def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "content": f"{prompt}"})

    stream = co.chat(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    response = ""

    for event in stream:
        if hasattr(event, 'event_type') and event.event_type == "text-generation":
            response += event.text
        elif isinstance(event, tuple) and len(event) == 2 and event[0] == 'text':
            response += event[1]

    response = response.replace("\n", "").strip()
    response = response.split(",")
    response = [i.strip() for i in response]

    temp = []
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
                break
    
    response = temp

    if not response or "(query)" in str(response):
        # Fallback to general query
        return [f"general {prompt}"]
    
    return response

if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))