import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars["CohereAPIKey"]

co = cohere.Client(api_key=CohereAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. Your response must be a comma-separated list of commands. ***

**General Queries:**
- Respond with 'general (query)' if a query can be answered by a large language model (LLM) and doesn't require real-time information. Examples:
    - 'who was akbar?' -> 'general who was akbar?'
    - 'how can i study more effectively?' -> 'general how can i study more effectively?'
    - 'can you help me with this math problem?' -> 'general can you help me with this math problem?'
    - 'Thanks, i really liked it.' -> 'general thanks, i really liked it.'
    - 'what is python programming language?' -> 'general what is python programming language?'
- Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete, even if it might seem to require up-to-date information. Examples:
    - 'who is he?' -> 'general who is he?'
    - 'what's his networth?' -> 'general what's his networth?'
    - 'tell me more about him.' -> 'general tell me more about him.'
- Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc. Examples:
    - 'what's the time?' -> 'general what's the time?'

**Real-time Queries:**
- Respond with 'realtime (query)' if a query cannot be answered by an LLM alone and requires up-to-date information from the internet. Examples:
    - 'who is indian prime minister' -> 'realtime who is indian prime minister'
    - 'tell me about facebook's recent update.' -> 'realtime tell me about facebook's recent update.'
    - 'tell me news about coronavirus.' -> 'realtime tell me news about coronavirus.'
    - 'who is akshay kumar' -> 'realtime who is akshay kumar'
    - 'what is today's news?' -> 'realtime what is today's news?'
    - 'what is today's headline?' -> 'realtime what is today's headline?'

**Application/System Commands:**
- **Open Application/Website**: Respond with 'open (application name or website name)'. For multiple, use 'open 1st application name, open 2nd application name'. Examples:
    - 'open facebook' -> 'open facebook'
    - 'open chrome and firefox' -> 'open chrome, open firefox'
- **Close Application**: Respond with 'close (application name)'. For multiple, use 'close 1st application name, close 2nd application name'. Examples:
    - 'close notepad' -> 'close notepad'
- **Play Song**: Respond with 'play (song name)'. For multiple, use 'play 1st song name, play 2nd song name'. Examples:
    - 'play afsanay by ys' -> 'play afsanay by ys'
- **Generate Image**: Respond with 'generate image (image prompt)'. For multiple, use 'generate image 1st image prompt, generate image 2nd image prompt'. Examples:
    - 'generate image of a lion' -> 'generate image of a lion'
- **Set Reminder**: Respond with 'reminder (datetime with message)'. Example:
    - 'set a reminder at 9:00pm on 25th june for my business meeting.' -> 'reminder 9:00pm 25th june business meeting'
- **System Control**: Respond with 'system (task name)' for actions like mute, unmute, volume up, volume down. For multiple, use 'system 1st task, system 2nd task'. Examples:
    - 'mute the volume' -> 'system mute'
- **Content Writing**: Respond with 'content (topic)' for writing applications, codes, emails, essays, etc. For multiple, use 'content 1st topic, content 2nd topic'. Examples:
    - 'write an application for sick leave' -> 'content application for sick leave'
- **Google Search**: Respond with 'google search (topic)'. For multiple, use 'google search 1st topic, google search 2nd topic'. Examples:
    - 'google search latest AI news' -> 'google search latest AI news'
- **YouTube Search**: Respond with 'youtube search (topic)'. For multiple, use 'youtube search 1st topic, youtube search 2nd topic'. Examples:
    - 'youtube search python tutorials' -> 'youtube search python tutorials'

**Combined Commands:**
- If the query asks to perform multiple tasks, combine them with commas. Example:
    - 'open facebook, telegram and close whatsapp' -> 'open facebook, open telegram, close whatsapp'

**Ending Conversation:**
- If the user is saying goodbye or wants to end the conversation, respond with 'exit'. Example:
    - 'bye jarvis.' -> 'exit'

**Fallback:**
- Respond with 'general (query)' if you cannot decide the type of query or if it asks to perform a task not listed above.
"""

ChatHistory = [
    {"role": "User", "message": "how are you ?"},
    {"role": "Chatbot", "message": "general how are you ?"},
    {"role": "User", "message": "do you like pizza ?"},
    {"role": "Chatbot", "message": "general do you like pizza ?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th at 11pm "},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "generate image of a cat and a dog"},
    {"role": "Chatbot", "message": "generate image of a cat, generate image of a dog"},
    {"role": "User", "message": "play some music and open youtube"},
    {"role": "Chatbot", "message": "play some music, open youtube"},
    {"role": "User", "message": "mute the system and close chrome"},
    {"role": "Chatbot", "message": "system mute, close chrome"}
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