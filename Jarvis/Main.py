from Frontend.GUI import (
    GraphicalUserInterface,
    SetAsssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
    AttachToDefaultDesktop,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IronManFeatures import (
    GetSystemDiagnostics,
    GetWeatherReport,
    GetOverheadTracking,
    GetTacticalDossier,
    GenerateSchematic,
    JarvisVision,
)
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f""" {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you? """

functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
subprocess_list = []



# Ensure a default chat log exists if no chats are logged
def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as temp_file:
                    temp_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                    response_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json file not found. Creating default response.")
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

# Read chat log from JSON
def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        print("ChatLog.json not found.")
        return []

# Integrate chat logs into a readable format


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

    # Ensure the Temp directory exists
    temp_dir_path = TempDirectoryPath('')  # Get the directory path
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Display the chat on the GUI
def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if len(str(data)) > 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(data)
    except FileNotFoundError:
        print("Database.data file not found.")

# Initial execution setup
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

# Main execution logic
def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAsssistantStatus("Listening...")
        Query = SpeechRecognition()
        if not Query or not str(Query).strip():
            SetAsssistantStatus("Available...")
            return False

        ShowTextToScreen(f"{Username}: {Query}")
        SetAsssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)

        print(f"\nDecision: {Decision}\n")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Merged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )

        # Iron Man Superpowers Dispatch
        for queries in Decision:
            if "diagnostics" in queries:
                SetAsssistantStatus("Analyzing Telemetry...")
                Answer = GetSystemDiagnostics()
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "weather" in queries:
                SetAsssistantStatus("Scanning Atmosphere...")
                Answer = GetWeatherReport()
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "overhead" in queries:
                SetAsssistantStatus("Tracking Radar...")
                Answer = GetOverheadTracking()
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif queries.startswith("tactical"):
                SetAsssistantStatus("Accessing Intel...")
                topic = queries.replace("tactical", "").strip()
                Answer = GetTacticalDossier(topic)
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif queries.startswith("vision"):
                SetAsssistantStatus("Visual Perception...")
                v_query = queries.replace("vision", "").strip()
                source = "camera" if ("camera" in v_query.lower() or "webcam" in v_query.lower()) else "screen"
                Answer = JarvisVision(source=source, query=v_query if v_query else "Describe what you see.")
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "generate image" in queries or "generate schematic" in queries:
                SetAsssistantStatus("Synthesizing Schematic...")
                p_text = queries.replace("generate image", "").replace("generate schematic", "").strip()
                Answer = GenerateSchematic(p_text)
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if G and R or R:
            SetAsssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAsssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        else:
            for queries in Decision:
                if "general" in queries:
                    SetAsssistantStatus("Thinking...")
                    QueryFinal = queries.replace("general", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                elif "realtime" in queries:
                    SetAsssistantStatus("Searching...")
                    QueryFinal = queries.replace("realtime", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                elif "exit" in queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAsssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    os._exit(1)
    except Exception as e:
        print(f"Error in MainExecution: {e}")
    finally:
        SetAsssistantStatus("Available...")

# Thread for primary execution loop
def FirstThread():
    sleep(1.5)
    last_mic = None
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()

            if CurrentStatus.lower() == "true":
                if last_mic != "true":
                    print("\n[Microphone Active] Listening for voice command...")
                    last_mic = "true"
                MainExecution()
                last_mic = "false"
            elif CurrentStatus.lower() == "false":
                if last_mic != "false":
                    print("[Assistant Ready] Microphone is idle. Click the mic button on GUI to speak.")
                    last_mic = "false"
                AIStatus = GetAssistantStatus()
                if "Available..." not in AIStatus:
                    SetAsssistantStatus("Available...")
                sleep(0.3)
            else:
                sleep(0.5)
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            sleep(1)



# Thread for GUI execution
def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

# Entry point
if __name__ == "__main__":
    AttachToDefaultDesktop()
    InitialExecution()
   
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()
    