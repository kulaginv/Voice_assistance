# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 18:41:00 2022

@author: Vasily
"""
# recognize and recorde speech
import pyttsx3
import speech_recognition as sr

# matematical things
import numpy as np
import random  # генератор случайных чисел

# make "beep" sounds
import winsound

# read xml files
from lxml import etree

# clear data (remove useless words)
from nltk import word_tokenize
from nltk.corpus import stopwords

# mel spectrograme 
import librosa

# remove warning
import warnings
warnings.filterwarnings("ignore")

# translator
from googletrans import Translator

# open web browser
import webbrowser

# get real data and time
import datetime

# information about weather
from pyowm import OWM

# get jokes
import pyjokes
#from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)

# neural network
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout



class voiceAssistance:  
    
    name = ''
    language = ''
    sex = ''
    name_said = False
    first = False
    go_sleep = False

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
    tts.setProperty('volume', 1     )
    tts.setProperty('rate', 150)
    


def record_audio(timeout=4, phrase_time_limit=5):
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
            if voiceAssistance.first and voiceAssistance.name_said: 
                greetings()
                voiceAssistance.first = False
            #say('Чем я могу помочь ?')
            print("Listening...")
            if voiceAssistance.name_said:
                winsound.Beep(1000, 500)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            with open("microphone-result.wav", "wb") as file:
                file.write(audio.get_wav_data())
            voiceAssistance.name_said = False

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
    t_day = translator.translate(time_of_day(), dest = voiceAssistance.language)
    gr = [
        Traduction.get("greetings").format(Me.name),
        Traduction.get("greetings_day").format(t_day.text, Me.name)
    ]
    say(gr[random.randint(0, len(gr) - 1)])
    
    
def farewell(*args):
    t_day = translator.translate(time_of_day(), dest = voiceAssistance.language)
    fr = [
        Traduction.get("farewell").format(Me.name),
        Traduction.get("farewell_day").format(Me.name, t_day.text)
        ]
    say(fr[random.randint(0, len(fr) - 1)])
    voiceAssistance.go_sleep = True
    
    
def time_of_day():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<4:
        return 'night'
    
    elif hour>= 4 and hour<12:
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
    if args: 
        town = args[0][0]
        city = translator.translate(town)
        city = city.text
    else: 
        city = Me.location
        town = city
    try:
        owm = OWM('d90b7a75bc7a523021d2719e2c3de7a6')
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather
    except: return
    weather_status = w.detailed_status
    status = translator.translate(weather_status, dest = voiceAssistance.language)
    status = status.text
    weather_wind = w.wind()["speed"]
    weather_temperature = w.temperature('celsius')["temp"]

    
    print("Weather in " + city + " : " + weather_status + 
          "\nTemperature is : " + str(weather_temperature) + " (Celsius)"
          "\nSpeed of wind is : " + str(weather_wind) + " (m/sec)")
    say(Traduction.get('weather').format(town, status, weather_temperature, weather_wind))
    
    
def jokes(*args):
    joke_init = pyjokes.get_joke()
    print(joke_init)
    joke = translator.translate(joke_init, dest = voiceAssistance.language)
    joke = joke.text
    print(joke)
    say(joke)


def clean_sens(text):
    if voiceAssistance.language == 'en':
        stop_words = stopwords.words('english')
    elif voiceAssistance.language == 'fr':
        stop_words = stopwords.words('french')
    else: stop_words = stopwords.words('russian')
    
    token = word_tokenize(text)
    cleaned_token = []
    for word in token:
        if word not in stop_words:
            cleaned_token.append(word)
    return cleaned_token


def say_name(*args):
    names = ['alisa','alice','алиса']
    name = False
    while not name:
        phrase = record_audio(timeout=0, phrase_time_limit=None)
        phrase = clean_sens(phrase)
        if phrase:
            print(phrase)
        for i in range(len(phrase)):
            if phrase[i] in names:
                name = True
                break   
    voiceAssistance.name_said = True
    
def no_command(*args):
    pass
    

def init_model():
    model = Sequential()
    model.add(Dense(256, input_shape=(128,)))
    model.add(Dense(256, activation="relu"))
    model.add(Dropout(0.25))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.25))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.25))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.25))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss="binary_crossentropy", metrics=["accuracy"], optimizer="adam")
    return model

def get_mel_feature(file_name):
    X, sample_rate = librosa.load(file_name)
    result = np.array([])
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
    result = np.hstack((result, mel))
    return result

def sex_recognition(*args):
    say('Скажите любое предложение')
    record_audio()
    features = get_mel_feature('microphone-result.wav').reshape(1, -1)
    male = model.predict(features)[0][0]
    female = 1 - male
    gender = "male" if male > female else "female"
    if gender == 'male': say(f'По моим подсчетам, вы с вероятностью {male*100:.2f}% являетесь мужчиной')  
    else: say(f'По моим посчетам, вы с вероятностью {female*100:.2f}% являетесь девушкой')
    print("Result:", gender)
    print(f"Probabilities: Male: {male*100:.2f}%    Female: {female*100:.2f}%")

commands = {
    ("bonjour", "salut", "hello", "hi", "morning", "привет", "здравствуй"): greetings,
    ("goodbye", "bye", "пока"): farewell,
    ("громче"): say_louder,
    ("тише"): say_quieter,
    ("быстрее"): say_faster,
    ("медленнее"): say_slower,
    ("обычная"): default_volum_speed,
    ("time", "время"): time_now,
    ("joke", "шутка", "расскажи шутку", "скажи шутку"): jokes,
    ("search","google","найди"): browser_search,
    ("премьер"): premier_search,
    ("weather","show weather", "погода", "temps"): weather,
    ('определи', 'voix'): sex_recognition,
    ("no command"): no_command
}


def command_search(text):
    for key in commands.keys():
        for i in range(1,len(voice_input)+1):
            if " ".join(voice_input[:i]) in key:
                command = " ".join(voice_input[:i])
                command_options = [str(option) for option in voice_input[i:len(voice_input)]]
                return command, command_options
    return 'no command', ''
            


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
    voiceAssistance.language = 'ru'
    
    
    tts = pyttsx3.init()
    define_voice()
    default_volum_speed()
    tree = etree.parse("traduction.xml")
    translator = Translator()
    model = init_model()
    model.load_weights("data/model.h5")

    # старт записи речи с последующим выводом распознанной речи
    voiceAssistance.first = True 
    while(not voiceAssistance.go_sleep):
        say_name()
        voice_input = record_audio(timeout=4, phrase_time_limit=5)
        print(voice_input)
        voice_input = clean_sens(voice_input)
        if voice_input: 
            if len(voice_input) == 1:
                command = voice_input[0]
                command_definition(command)
            else:
                command, command_options = command_search(voice_input)
                command_definition(command, command_options)

            
            


        
    
    
    