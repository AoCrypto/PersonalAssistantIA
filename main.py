import speech_recognition as sr
import pyttsx3
import datetime
import locale
import asyncio
import subprocess
import pyautogui
import wikipedia
import re
from roman_arabic_numerals import conv 
import psutil
import struct
import pvporcupine
from googlesearch import search
import webbrowser
import pyvolume
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from modules.ollama_nlp import OllamaNLP
import transformers

# Initialisation du modèle Ollama
ollam_nlp = OllamaNLP()

# Fonction pour générer une réponse en utilisant le modèle Ollama
def generate_response(user_input):
    # Utilisez le modèle Ollama pour générer une réponse
    response = ollam_nlp.generate_text(prompt = user_input, model = 'mistral')
    return response

sr.Microphone(device_index=7)

# Initialiser le recognizer
r = sr.Recognizer()

# Initialiser le synthétiseur
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")

# Fonction pour parler
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Fonction pour écouter
def listen():
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        audio = r.listen(source)
        print("Fin de l'écoute.")
    try:
        print("Reconnaissance du texte...")
        text = r.recognize_google(audio, language="en-EN")
        print(f"Utilisateur : {text}")
        return text.lower()
    except Exception as e:
        print(e)
        return ""

# Boucle principale de l'assistant
def main():
    while True:
        # Écoutez l'entrée de l'utilisateur
        command = input()
        if "launch" in command:
            command = command.replace("launch","")
            pyautogui.press('super')
            pyautogui.sleep(1)
            pyautogui.typewrite(command)
            pyautogui.press("enter")
            response = generate_response(command)

        if 'time'in command:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%H:%M")
            speak(f"Right now it's {formatted_time}")

        if 'volume'in command:
            devices = AudioUtilities.GetSpeakers()
            level = int(re.search(r'\d+', command).group())
            if level < 0 or level > 100 :
                speak("no")
            else :
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar( level / 100, None)  
            
        elif 'search' in command:
            command = command.replace("search","")
            url = f"https://www.google.com/search?q={command}"
            webbrowser.open(url)
            response = generate_response(command)

        else :
            response = generate_response(command)

        # Faites parler l'assistant
        print(response)
        speak(response)
        
# Exécutez la fonction principale
if __name__ == "__main__":
    main()