from ddgs import DDGS
from groq import Groq
from json import load, dump
import datetime
import requests
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = None
if GroqAPIKey and "enter your key" not in GroqAPIKey.lower():
    try:
        client = Groq(api_key=GroqAPIKey)
    except Exception as e:
        print(f"Warning: Failed to initialize Groq client: {e}")

System = f"""Hello, I am {Username}. You are {Assistantname}, an advanced AI assistant equipped with real-time, live internet access.
*** Always answer the user's question accurately using the live internet search results provided below. ***
*** Prioritize exact dates, company event programs, schedules, medical facts, or recent developments from the search data. ***
*** Answer concisely and professionally in 2 to 4 clear sentences. Do not mention that you performed a search; speak directly and authoritatively. ***
"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except Exception:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def LiveWebSearch(query):
    """Performs real-time web search using DuckDuckGo with Google fallback (100% free, no API key)."""
    data = []

    # 1. Primary engine: DuckDuckGo (fast, unblocked, current)
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=5))
        for r in results:
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            if title or body:
                data.append(f"Source: {title}\nDetails: {body}")
    except Exception as e:
        print(f"Notice: DDGS search fallback: {e}")

    # 2. Secondary fallback: Google Search
    if not data:
        try:
            from googlesearch import search
            results = list(search(query, advanced=True, num_results=4))
            for r in results:
                if r.title or r.description:
                    data.append(f"Source: {r.title}\nDetails: {r.description}")
        except Exception as e:
            print(f"Notice: Google search fallback: {e}")

    if not data:
        return f"No real-time search results found for '{query}'."

    Answer = f"Real-Time Internet Search Results for '{query}':\n[start]\n"
    Answer += "\n\n".join(data)
    Answer += "\n[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": f"Hello {Username}, I am online and ready to assist you."}
]

def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = (
        f"Real-Time System Timestamp:\n"
        f"Day: {day}, Date: {date} {month} {year}, Time: {hour}:{minute}:{second}.\n"
    )
    return data

def RealtimeSearchEngine(prompt):
    """Searches live internet data and synthesizes an intelligent answer via Groq."""
    global SystemChatBot, messages, client

    if not client:
        env_vars = dotenv_values(".env")
        key = env_vars.get("GroqAPIKey", "")
        if key and "enter your key" not in key.lower():
            try:
                client = Groq(api_key=key)
            except Exception as e:
                print(f"Error initializing Groq: {e}")
        if not client:
            return "Please set your GroqAPIKey in the .env file to enable real-time search."

    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
    except Exception:
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})

    # Fetch live web results
    search_context = LiveWebSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_context})

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            max_tokens=512,
            temperature=0.4,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Search engine synthesis error: {e}")
        return f"An error occurred while synthesizing search results: {str(e)}"
    finally:
        if SystemChatBot and SystemChatBot[-1]["role"] == "system" and "Real-Time Internet Search" in SystemChatBot[-1]["content"]:
            SystemChatBot.pop()

if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))