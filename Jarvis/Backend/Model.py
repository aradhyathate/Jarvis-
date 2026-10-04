import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey", "")

co = None
if CohereAPIKey and "enter your key" not in CohereAPIKey.lower():
    try:
        co = cohere.Client(api_key=CohereAPIKey)
    except Exception as e:
        print(f"Warning: Failed to initialize Cohere client: {e}")

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "diagnostics", "weather",
    "overhead", "tactical", "vision"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'diagnostics' if a query is asking for system status, armor status, battery level, hardware diagnostics, CPU or RAM telemetry like 'report system status', 'how is the armor holding up?', 'system diagnostics', 'what is my battery percentage?', 'check telemetry', etc.
-> Respond with 'weather' if a query is asking about weather, atmospheric conditions, flight radar, wind velocity, rain, or barometric pressure like 'what's the weather?', 'atmospheric conditions for flight', 'weather report', 'flight conditions', 'is it raining?', 'how is the wind?', etc.
-> Respond with 'overhead' if a query is asking to scan airspace, track aircraft, track satellites, or locate the International Space Station like 'scan airspace', 'any aircraft overhead?', 'track satellite', 'where is the ISS?', 'airspace radar', 'check satellites', etc.
-> Respond with 'tactical (topic)' if a query is asking for a tactical briefing, dossier, or background intelligence on a weapon, aircraft, technology, military asset, or entity like 'tactical dossier on F-22', 'intelligence briefing on quantum computing', 'dossier on Elon Musk', etc.
-> Respond with 'vision (question or instruction)' if a query is asking to look at the screen, inspect the webcam, analyze code on screen, or see something visually like 'what is on my screen?', 'look at this', 'see through camera', 'who is in front of the camera?', 'read what is on screen', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate schematic of arc reactor', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
    {"role": "User", "message": "how are you ?"},
    {"role": "Chatbot", "message": "general how are you ?"},
    {"role": "User", "message": "report system status and armor telemetry"},
    {"role": "Chatbot", "message": "diagnostics"},
    {"role": "User", "message": "what are the flight conditions and weather outside?"},
    {"role": "Chatbot", "message": "weather"},
    {"role": "User", "message": "scan airspace for any aircraft overhead"},
    {"role": "Chatbot", "message": "overhead"},
    {"role": "User", "message": "give me a tactical dossier on F-22 Raptor"},
    {"role": "Chatbot", "message": "tactical F-22 Raptor"},
    {"role": "User", "message": "look at my screen and tell me what you see"},
    {"role": "Chatbot", "message": "vision what is on my screen"},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test"):
    global co
    if not co:
        env_vars = dotenv_values(".env")
        key = env_vars.get("CohereAPIKey", "")
        if key and "enter your key" not in key.lower():
            try:
                co = cohere.Client(api_key=key)
            except Exception as e:
                print(f"Cohere init error: {e}")
        if not co:
            print("Notice: Cohere API key missing or invalid in .env. Defaulting query to general chat.")
            return [f"general {prompt}"]

    messages.append({"role": "user", "content": f"{prompt}"})

    try:
        stream = co.chat(
            model='command-r-08-2024',
            message=prompt,
            temperature=0.3,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )

        response = ""
        if hasattr(stream, 'text') and stream.text:
            response = stream.text
        else:
            for event in stream:
                if isinstance(event, tuple) and event[0] == 'text':
                    response = event[1]
                elif hasattr(event, 'text'):
                    response += event.text
    except Exception as e:
        print(f"Cohere Decision Model error: {e}. Defaulting to general query.")
        return [f"general {prompt}"]

    response = response.replace("\n", "")
    response = response.split(",")

    response = [i.strip() for i in response]

    temp = []

    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    
    response = temp

    if not response or "(query)" in str(response):
        return [f"general {prompt}"]
    else:
        return response

    
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>>")))