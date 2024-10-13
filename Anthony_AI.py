from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from imaginairy.utils.log_utils import configure_logging
from imaginairy.schema import ImaginePrompt
from llm_axe import OllamaChat, OnlineAgent
from modules.ollama_nlp import OllamaNLP
from imaginairy.api import imagine
from ctypes import cast, POINTER
import speech_recognition as sr
import matplotlib.pyplot as plt
from comtypes import CLSCTX_ALL
from tkinter import filedialog
from jokeapi import Jokes
import pygetwindow as gw
from tkinter import Tk
from PIL import Image
import numpy as np
import pyautogui
import datetime
import easyocr
import pyttsx3
import pyjokes
import asyncio
import psutil
import fitz
import time
import sys
import os
import re

ollam_nlp = OllamaNLP()

def generate_response(user_input):
    reponse = ollam_nlp.generate_text(
        prompt=
f"""Tu es un assistant personnel inspiré de JARVIS du film Iron Man, tu es capable d'effectuer certaines tâches. 
Tu t'appeles Anthony et ton objectif est de répondre à toutes mes demandes, tu ne dois jamais te présenter sauf si je te le demande. 
Tu ne dois jamais écrire les balises que tu utilises pour me répondre. 
Voici une de mes demandes : {user_input}""", model='llama3')
    return reponse

r = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('voice', "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_frFR_HortenseM")

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        audio = r.listen(source)
        print("Fin de l'écoute.")
    try:
        print("Reconnaissance du texte...")
        text = r.recognize_google(audio, language="fr-FR")
        print(f"Utilisateur : {text}")
        return text.lower()
    except Exception as e:
        print(e)
        return ""

async def print_joke():
    j = await Jokes()
    joke = await j.get_joke(lang="fr")
    if joke["type"] == "single":
        return joke["joke"]
    else:
        debut = joke["setup"]
        fin = joke["delivery"]
        blague_entiere = f"{debut} {fin}"
        return blague_entiere

def control_media(command):
    if "play" in command :
        pyautogui.press("playpause")
    elif "pause"  in command :
        pyautogui.press("playpause")
    elif "next" in command :
        pyautogui.press("nexttrack")
    elif "previous" in command :
        pyautogui.press("prevtrack")
        pyautogui.press("prevtrack")
    elif "debut" in command :
        pyautogui.press("prevtrack")

def get_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M")
    return formatted_time

def screenshot():
    im1 = pyautogui.screenshot()
    im1.save('screenshot.png')
    img1 = Image.open('screenshot.png')
    img1.show()

chat_memory = []

long_term_memory = []

async def anthony_ai(command):

    choice = ollam_nlp.generate_text(
        prompt=f"""Réponds avec une seule phrase concise, sans explication ni balise. Tu ne dois pas te tromper sur l'ortographe de la valeur que tu renvois
Choisis parmi les options suivantes en fonction de la demande de l'utilisateur :
- 'Control_sound' pour contrôler le son
- 'Screenshot' pour prendre une capture d'écran
- 'Launch' suivi du nom de l'application pour l'ouvrir
- 'Gen_image' pour générer ou créer ou dessiner une image
- 'Psu_bat' pour des informations sur la batterie
- 'Jokes' pour une blague
- 'Control_music' suivi de 'play', 'pause', 'next', 'previous' ou 'beginning' pour contrôler la musique
- 'Ocr' pour extraire du texte d'un PDF
- 'Time' pour l'heure actuelle
- 'Web_search' pour effectuer une recherche internet afin d'avoir des informations en plus
- 'text' pour répondre si aucune des fonctions précédentes ne s'appliquent
- 'Add_to_memory' pour ajouter des informations sur la mémoire à long terme
Fais ceci avec cette phrase : {command}
Voilà le contexte de la discussion, cela peut être utile pour faire ton choix : {memory}""",
        model="llama3"
    )
    print(choice)

    memory.append(command)
    if 'Launch' in choice:
        app_name = choice.replace("launch", "").strip()
        pyautogui.press('super')
        pyautogui.sleep(1)
        pyautogui.typewrite(app_name)
        pyautogui.press("enter")
        reponse = generate_response(command) 
        return reponse 

    if 'Screenshot' in choice :
        screenshot()
        reponse = generate_response(command)
        return reponse

    elif 'Control_sound' in choice:
        devices = AudioUtilities.GetSpeakers()
        level = int(re.search(r'\d+', command).group())
        if 0 < level <= 100:
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
        if level == 0 :
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
        reponse = generate_response(command)
        return reponse

    elif 'Web_search' in choice:
        llm = OllamaChat(model="llama3")
        online_agent = OnlineAgent(llm)
        an_prompt = ollam_nlp.generate_text(prompt=
f"""Traduis cette phrase en anglais et optimisez-la pour une recherche : {command}""",
model="llama3")
        reponse = online_agent.search(an_prompt)
        print(reponse)
        answer_question = ollam_nlp.generate_text(prompt=
f""" Réponds à la question de l'utilisateur en français, en utilisant les unités du système métrique : {command}. 
Utilisez les informations suivantes : {reponse}""", model='llama3')
        return answer_question

    if 'Gen_image' in choice:
        configure_logging()
        prompt_gen_image = ollam_nlp.generate_text(prompt=
f"""tu dois générer un prompt adéquat afin de générer une image selon la demande de l'utilisateur sans poser de question.
tu dois écrire ce prompt en anglais, ne jamais l'introduire et ne surtout jamais l'expliquer. N'écris jamais "Here is the prompt:"
Voilà la demande de l'utilisateur, à toi de faire le prompt en suivant mes instructions : {command}""", model='llama3')
        prompts = [ImaginePrompt(prompt_gen_image)]
        for result in imagine(prompts):
            img = result.img
            file_name = f"generated_image_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            img.save(os.path.join(os.getcwd(), file_name))  # sauvegarde l'image dans le répertoire courant
            img1 = Image.open(file_name)
            img1.show()  # affiche l'image
            return "Image générée avec succès!"
            print("c'est bon")

    if 'Psu_bat' in choice :
        battery = psutil.sensors_battery()
        seconds_approximation = battery.secsleft
        percent = battery.percent
        plugged = battery.power_plugged
        reponse = ollam_nlp.generate_text(prompt=
f"""Tu dois me donner des informations sur ma batterie en francais, et tu ne dois surtout pas écrire tes balises. 
Voilà les informations que tu peux utiliser : 
-   {percent} qui est le pourcentage de batterie restante et utilisable 
-   {seconds_approximation} qui est une aproximation en secondes de la durée d'utilisation restante, tu dois donner le résultats en secondes et en minutes, sans expliquer la conversion. 
Fais attention aux unités.""",
model='llama3')
        print(reponse)
        return reponse

    if 'Jokes' in choice :
        blague = await print_joke()
        return blague

    if 'Control_music' in choice :
        if not gw.getWindowsWithTitle('Spotify'):
            pyautogui.press('super')
            pyautogui.sleep(1)
            pyautogui.typewrite('Spotify')
            pyautogui.press("enter")
            pyautogui.sleep(5)
        control_media(choice)
        response = generate_response(command)
        return response

    if 'Ocr' in choice :
        reader = easyocr.Reader(['en', 'fr'])
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
        doc = fitz.open(file_path)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pixmap = page.get_pixmap()
            img_data = pixmap.tobytes("png")
            result = reader.readtext(img_data)
            text = ' '.join([item[1] for item in result])
            print(text)
        response = ollam_nlp.generate_text(prompt=
f"""L'utilisateur vient de te faire une demande qui nécessite que tu utilise des informations issus d'un pdf. Voici la demande {command}.
Voici le fichier que tu dois utiliser pour répondre, tu répondras toujours en francais {text}""", model = 'llama3')
        return response

    if 'Time' in choice :
        temps = get_time()
        response =ollam_nlp.generate_text(prompt=
f"""Tu dois dire l'heure qu'il est en utilisant ces informations {temps}""", model = 'llama3')
        return response

    if 'text' in choice :
        response = ollam_nlp.generate_text(prompt =
f"""Tu dois répondre à cette demande : {command}. Le contexte de la conversation peut t'être utile, le voici : {memory}""", model='llama3')
        return response
