# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 18:41:00 2022

@author: Vasily
"""
import pyttsx3
import speech_recognition as sr
from lxml import etree

import webbrowser
import random  # генератор случайных чисел
import datetime
from pyowm import OWM
import pyjokes
#from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)


class voiceAssistance:  
    
    name = ''
    language = ''
    sex = ''

class Me:
    name = 'vasily'
    location = 'grenoble'
    sex = 'male'
    
        
class Traduction:
    """
    Получение вшитого в приложение перевода строк для создания мультиязычного ассистента
    """
    traduction = etree.parse("traduction.xml")

    def get(text: str):
        """
        Получение перевода строки из файла на нужный язык (по его коду)
        :param text: текст, который требуется перевести
        :return: вшитый в приложение перевод текста
        """
        for phrase in tree.xpath("/database/phrase"):
            if phrase.attrib['name'] == text :
                return phrase.find(voiceAssistance.language).text
        else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возврат исходного текста
            #print(colored("Not translated phrase: {}".format(text), "red"))
            return text


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
            recognized_data = recognizer.recognize_google(audio, language=voiceAssistance.language).lower()

        except sr.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит выброс ошибки
        except sr.RequestError:
            print("Check your Internet Connection, please")

        return recognized_data
    
    
def greetings(*args):
    gr = [
        Traduction.get("greetings").format(Me.name),
        Traduction.get("greetings_day").format(time_of_day(), Me.name)
    ]
    say(gr[random.randint(0, len(gr) - 1)])
    
    
def farewell(*args):
    fr = [
        Traduction.get("farewell").format(Me.name),
        Traduction.get("farewell_day").format(Me.name, time_of_day())
        ]
    say(fr[random.randint(0, len(fr) - 1)])
    
    
def time_of_day():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        return 'morning'
  
    elif hour>= 12 and hour<18:
        return 'afternoon'  
  
    else:
        return 'evening'    
    
    
def time_now(*args):
    say(Traduction.get('time').format(int(datetime.datetime.now().hour), 
                                      int(datetime.datetime.now().minute), 
                                      int(datetime.datetime.now().second)))
    
def browser_search(*args):
    if not args: return
    request = " ".join(args[0])
    url = "https://duckduckgo.com/?q="+request
    webbrowser.open(url)
    
def premier_search(*args):
    if not args: return
    request = " ".join(args[0])
    url = "https://premier.one/search?query="+request
    webbrowser.open(url)
    
    
def weather(*args):
    if args[0]: city = args[0][0]
    else: city = Me.location
    try:
        owm = OWM('d90b7a75bc7a523021d2719e2c3de7a6')
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather
    except: return
    
    weather_status = w.detailed_status 
    weather_wind = w.wind()["speed"]
    weather_temperature = w.temperature('celsius')["temp"]
    
    print("Weather in " + city + " : " + weather_status + 
          "\nTemperature is : " + str(weather_temperature) + " (Celsius)"
          "\nSpeed of wind is : " + str(weather_wind) + " (m/sec)")
    say(Traduction.get('weather').format(city, weather_status, weather_temperature, weather_wind))
    
    
    
def jokes(*args):
    say(pyjokes.get_joke())




commands = {
    ("bonjour", "salut", "hello", "hi", "morning", "привет", "здравствуй"): greetings,
    ("goodbye", "bye", "пока"): farewell,
    ("time", "время"): time_now,
    ("search","google","найди"): browser_search,
    ("премьер"): premier_search,
    ("weather", "погода"): weather,
    ("joke", "шутка"): jokes,
}



def command_definition(command_name: str, *args):
    """
    Выполнение заданной пользователем команды и аргументами
    :param command_name: название команды
    :param args: аргументы, которые будут переданы в метод
    :return:
    """
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass  # print("Command not found")
            

if __name__ == '__main__': 
    
    voiceAssistance = voiceAssistance()
    voiceAssistance.name = 'kira'
    voiceAssistance.sex = 'female'
    voiceAssistance.language = 'en'
    
    tts = pyttsx3.init()
    define_voice()
    default_volum_speed()
    tree = etree.parse("traduction.xml")

    # старт записи речи с последующим выводом распознанной речи
    voice_input = record_audio()
    print(voice_input)
    if voice_input: 
        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = [str(option) for option in voice_input[1:len(voice_input)]]
        command_definition(command, command_options)

        
    
    
    