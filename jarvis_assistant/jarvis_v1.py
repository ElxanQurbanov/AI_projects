import os
import asyncio
import edge_tts
import pygame
import time
import speech_recognition as sr
import wikipedia
import pywhatkit
import webbrowser
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import keyboard


api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)



@tool
def play_youtube(query: str):
    """YouTube-da video oynadır."""
    pywhatkit.playonyt(query)
    return "Video başladıldı."

@tool
def google_search(query: str):
    """Google-da axtarış edir."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Google-da '{query}' axtarılır..."

@tool
def pc_control(action: str):
    """Kompüteri söndürür və ya yenidən başladır."""
    if action == "shutdown": os.system("shutdown /s /t 1")
    elif action == "restart": os.system("shutdown /r /t 1")
    return "Əmr yerinə yetirildi."

@tool
def wikipedia_search(query: str):
    """Wikipedia-da məlumat axtarır."""
    wikipedia.set_lang("az")
    try: return wikipedia.summary(query, sentences=2)
    except: return "Məlumat tapılmadı."

@tool
def open_google_earth(query: str = ""):
    """Google Earth-i açır. Əgər yer adı verilibsə, həmin yerə keçid edə bilər."""
    if query:
        # Opens specific location in web version of Google Earth
        url = f"https://earth.google.com/web/search/{query.replace(' ', '+')}"
    else:
        # Opens default Google Earth home
        url = "https://earth.google.com/web/"
    webbrowser.open(url)
    return "Google Earth açılır..."
tools = [play_youtube, google_search, pc_control, wikipedia_search, open_google_earth]

agent_executor = create_react_agent(model=llm, tools=tools)

async def speak(text):
    if not text.strip(): return 
    
    try:
        communicate = edge_tts.Communicate(text, "az-AZ-BabekNeural")
        await communicate.save("response.mp3")
        
        pygame.mixer.init()
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed('space'): 
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        pygame.mixer.quit()
    except Exception as e:
        print(f"[ERROR] TTS Failed: {e}")
        print(f"Jarvis (Text Only): {text}")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nDinləyirəm...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            text = r.recognize_google(audio, language="az-AZ")
            print(f"Siz: {text}")
            return text.lower()
        except:
            return ""

if __name__ == "__main__":

    system_prompt = (
        "Sən Jarvis-sən, Tony Stark-ın köməkçisi kimi ağıllı, sarkastik, amma çox faydalı bir süni intellekt köməkçisisən. "
        "Cavablarında qısa və professional ol. "
        "İstifadə edilə bilən alətlər: open_google_earth, wikipedia_search, google_search, play_youtube. "
        "Həmişə özünü Jarvis kimi təqdim et."
    )

    print("Jarvis aktivdir...")
    while True:
        cmd = listen()
        if "sağol" in cmd or "exit" in cmd:
            asyncio.run(speak("Sağ olun, cənab."))
            break
        
        if cmd:
            result = agent_executor.invoke({"messages": [
                ("system", system_prompt),
                ("user", cmd)
            ]})
            
            response = result["messages"][-1].content
            print(f"Jarvis: {response}")
            asyncio.run(speak(response))