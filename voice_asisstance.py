# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 18:41:00 2022

@author: Vasily
"""
import pyttsx3
import speech_recognition as sr


class voiceAssistance:  
    
    name = ''
    language = ''
    sex = ''
        
    
def define_voice():
    voices = tts.getProperty('voices')
    if voiceAssistance.language == 'fr':
        tts.setProperty('voice', voices[2].id)
    elif voiceAssistance.language == 'ru':
        tts.setProperty('voice', voices[0].id)
    elif voiceAssistance.language == 'en':
        if voiceAssistance.sex == 'male':
            tts.setProperty('voice', voices[3].id)
        else: tts.setProperty('voice', voices[1].id)
    
def say(text):
    tts.say(text)
    tts.runAndWait()

def say_louder():
    volume = tts.getProperty('volume')
    tts.setProperty('volume', volume+0.2)
    
def say_quieter():
    volume = tts.getProperty('volume')
    tts.setProperty('volume', volume-0.2)
    
def say_faster():
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate+80)
    
def say_slower():
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate-80)

def default_volum_speed():
    tts.setProperty('volume', 0.5)
    tts.setProperty('rate', 140)

def record_audio():
    """
    Enregistrement et reconnaissance audio
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        recognized_data = ""

        # régulation du bruit ambiant
        recognizer.adjust_for_ambient_noise(source, duration=3) 
        #duration: le nombre maximal de secondes pour lesquelles on ajustera dynamiquement le seuil avant de revenir

        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)

        except sr.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language='ru').lower()

        except sr.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит выброс ошибки
        except sr.RequestError:
            print("Check your Internet Connection, please")

        return recognized_data

if __name__ == '__main__': 
    
    voiceAssistance = voiceAssistance()
    voiceAssistance.name = 'Kira'
    voiceAssistance.sex = 'female'
    voiceAssistance.language = 'ru'
    
    tts = pyttsx3.init()
    define_voice()
    default_volum_speed()

    while True:
        # старт записи речи с последующим выводом распознанной речи
        text = 'Hello, my name is '+voiceAssistance.name
        voice_input = record_audio()
        print(voice_input)
        if voice_input: say("Вы сказали : "+voice_input)
    
    