# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 18:41:00 2022

@author: Vasily
"""
# recognize and recorde speech
import pyttsx3
import speech_recognition as sr

# offline recognition
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1) 

# to work with the operating system
import os

# to work with wave and json formats files
import wave
import json

# matematical things
import numpy as np
import random

# make "beep" sounds
import winsound

# read xml files
from lxml import etree

# clear data (remove useless words)
from nltk import word_tokenize
from nltk.corpus import stopwords

# package for music and audio analysis
import librosa

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
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #INFO, WARNING, and ERROR messages are not printed, 0 for all messages 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout



class voiceAssistance:  
    
    name = ''
    language = ''
    sex = ''
    name_said = False
    first = False
    go_sleep = False
    offline = False

class Me:
    name = 'vasily'
    location = 'paris'
    sex = 'male'
    
        
class Traduction:
    """
    Getting a line translation sewn into the application to create a multilingual assistant
    """
    traduction = etree.parse("traduction.xml")

    def get(text: str):
        """
        Getting a line translation from a file to the desired language
        :param text type str: the text to be translated
        :return: text translation 
        """
        for phrase in tree.xpath("/database/phrase"):
            if phrase.attrib['name'] == text :
                return phrase.find(voiceAssistance.language).text
            #else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возврат исходного текста
            #print(colored("Not translated phrase: {}".format(text), "red"))
        return text


def define_voice():
    """
    Choosing the language and gender of the assistant
    :return: None
    """
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
    """
    Pronounce the entered text
    :param text: text to read
    :return: None
    """
    tts.say(text)
    tts.runAndWait()

def say_louder():
    """
    Say the text louder
    :return: None
    """
    volume = tts.getProperty('volume')
    tts.setProperty('volume', volume+0.2)
    
def say_quieter():
    """
    Say the text quieter
    :return: None
    """
    volume = tts.getProperty('volume')
    tts.setProperty('volume', volume-0.2)
    
def say_faster():
    """
    Say the text faster
    :return: None
    """
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate+80)
    
def say_slower():
    """
    Say the text slower
    :return: None
    """
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate-80)

def default_volum_speed():
    """
    Default volum and speed
    :return: None
    """
    tts.setProperty('volume', 1)
    tts.setProperty('rate', 150)
    


def record_audio(timeout=4, phrase_time_limit=5):
    """
    Audio recording and recognition
    :param timeout: maximum number of seconds that this will wait for a phrase to start
    :param phrase_time_limit: maximum number of seconds that this will allow a phrase to continue
    :return:  recognized data
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
                command_definition("hi")
                voiceAssistance.first = False
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
            print("Offline recognitions")
            if not voiceAssistance.offline:
                say(Traduction.get('offline_text'))
            voiceAssistance.offline = True
            recognized_data = offline_recognition()

        return recognized_data
    

def offline_recognition():
    """
    Offline audio recognition
    :return: recognized data
    """
    recognized_data = ''
    try:
        wf = wave.open("microphone-result.wav", "rb")
        model = Model("offline/vosk-model-small-"+voiceAssistance.language)
        # download models: https://alphacephei.com/vosk/models
        offline_recognizer = KaldiRecognizer(model, wf.getframerate())

        while True:
            data = wf.readframes(1000)
            if len(data) == 0:
                break
            if offline_recognizer.AcceptWaveform(data):
                print(offline_recognizer.Result())
        recognized_data = json.loads(offline_recognizer.FinalResult())
    except:
        print("Sorry, speech service is unavailable. Try again later")
        
    return recognized_data["text"]
    

def greetings(*args):
    """
    Say the greeting phrase
    :param args: None
    :return: None
    """
    try:
        t_day = translator.translate(time_of_day(), dest = voiceAssistance.language)
        t_day = t_day.text
    except:
        t_day = time_of_day()
    gr = [
        Traduction.get("greetings").format(Me.name),
        Traduction.get("greetings_day").format(t_day, Me.name)
    ]
    say(gr[random.randint(0, len(gr) - 1)])
    
    
def farewell(*args):
    """
    Say the farewell phrase
    :param args: None
    :return: None
    """
    try:
        t_day = translator.translate(time_of_day(), dest = voiceAssistance.language)
        t_day = t_day.text
    except:
        t_day = time_of_day()
    fr = [
        Traduction.get("farewell").format(Me.name),
        Traduction.get("farewell_day").format(Me.name, t_day)
        ]
    say(fr[random.randint(0, len(fr) - 1)])
    voiceAssistance.go_sleep = True
    
    
def time_of_day():
    """
    Get the current time of day
    :return: the current time of day
    """
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
    """
    Get the current time
    :param args: None
    :return: None
    """
    say(Traduction.get('time').format(int(datetime.datetime.now().hour), 
                                      int(datetime.datetime.now().minute), 
                                      int(datetime.datetime.now().second)))
    
def browser_search(*args):
    """
    Search for information in the browser
    :param args: search keywords
    :return: None
    """
    if not args: return
    request = " ".join(args[0])
    url = "https://duckduckgo.com/?q="+request
    webbrowser.open(url)
    
def premier_search(*args):
    """
    Search for a series on the 'premier' service
    :param args: search keywords
    :return: None
    """
    if not args: return
    request = " ".join(args[0])
    url = "https://premier.one/search?query="+request
    webbrowser.open(url)
    
    
def weather(*args):
    """
    Get information about the weather in the city
    :param args: the city where you need to find out the weather
    :return: None
    """
    if args: 
        town = args[0][0]
        city = translator.translate(town)
        city = city.text
    else: 
        city = Me.location
        town = city
    try:
        #use my API KEY for openweathermap
        owm = OWM(os.getenv('WHEATHER_KEY'))
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather
    except: 
        say(Traduction.get('unavailable_service'))
        return
    
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
    """
    Listen to a joke
    :param args: None
    :return: None
    """
    joke_init = pyjokes.get_joke()
    print(joke_init)
    try:
        joke = translator.translate(joke_init, dest = voiceAssistance.language)
        joke = joke.text
        print(joke)
    except:
        joke = joke_init
    say(joke)


def clean_sens(text):
    """
    Clears the text from words that do not carry a semantic load
    :text args: the text that needs to be cleaned
    :return: cleared text
    """
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
    """
    Check if the assistant's name has been said
    :text args: heard text
    :return: None
    """
    names = ["alice", "alis", "alicia", "alison", "allie", "alisa", "алиса", "алис"]
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
    """
    The command was not found
    :text args: None
    :return: None
    """
    pass
    

def init_model():
    """
    Initialize a model for a neural network
    :return: ready-made model
    """
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
    """
    Mel-frequency spectrogram analysis
    :text file_name: audio file 
    :return: result of mel-frequency spectrogram analysis
    """
    X, sample_rate = librosa.load(file_name)
    result = np.array([])
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
    result = np.hstack((result, mel))
    return result

def sex_recognition(*args):
    """
    Determine gender by voice
    :text args: part of the data from the audio file 
    :return: definite gender
    """
    if len(args[0]) < 2:
        say(Traduction.get('say_phrase'))
        voiceAssistance.name_said = True
        record_audio()
    features = get_mel_feature('microphone-result.wav').reshape(1, -1)
    male = model.predict(features)[0][0]
    female = 1 - male
    gender = "male" if male > female else "female"
    try:
        sex = translator.translate(gender, dest = voiceAssistance.language)
        sex = sex.text
    except:
        sex = gender
    print("Result:", gender)
    print(f"Probabilities: Male: {male*100:.2f}%    Female: {female*100:.2f}%")
    if gender == 'male': say(Traduction.get("sex_recognition_result").format(round(male*100,2), sex))  
    else: say(Traduction.get("sex_recognition_result").format(round(male*100,2), sex))
    return gender
    
    
def change_language(*args):
    """
    Change the language
    :text args: None
    :return: None
    """
    voiceAssistance.name_said = True
    cur_lang = voiceAssistance.language
    say(Traduction.get('change_lang'))
    lang = record_audio()
    if lang in ['английский','english','anglais']: 
        voiceAssistance.language = 'en'
    elif lang in ['французский','french','français']: 
        voiceAssistance.language = 'fr'
    elif lang in ['русский','russian','russe']: 
        voiceAssistance.language = 'ru'
    else: say(Traduction.get('no_lang'))
    if voiceAssistance.language != cur_lang:
        define_voice()
        say(Traduction.get('new_lang'))

commands = {
    ("привет", "здравствуй", "доброе утро", "добрый день", "добрый вечер",
     "hello", "hi", "good morning", "good evening", "good night",
     "bonjour", "salut", "bonsoir" ): greetings,
    ("пока", "свидвния", "прощай",
     "goodbye", "bye", 
     "salut", "revoir", "adieu"): farewell,
    ("громче", "сделай громче", "прибавь громкость", "говори громче",
     "louder", "make louder", "say louder"
     "plus fort", "dis plus fort", "fait plus fort"): say_louder,
    ("тише", "сделай тише", "убавь громкость", "говори тише",
     "hush", "make quieter", "say quieter",
     "chut", "faire plus calme", "dire plus calme", "fait plus calme"): say_quieter, #bas
    ("быстрее", "скажи быстрее", "говори быстрее", "происноси слова быстрее",
     "faster", "say faster", "speak faster", "pronounce words faster",
     "plus vite", "dis plus vite", "parles plus vite", "prononces mots plus vite"): say_faster,
    ("медленнее", "скажи медленнее", "говори медленнее", "происноси слова медленнее",
     "slower", "say slower", "speak slower", "pronounce words slower",
     "moins vite", "dis moins vite", "parles moins vite", "prononces mots moins vite"): say_slower,
    ("обычная скорость", "обычная громкость", "изначальгые скорость громкость",
     "normal speed", "normal volume", "initial speed volume",
     "vitesse normale", "volume normal", "vitesse volume initiales"): default_volum_speed,
    ("время", "скажи время", "сколько времени", "который час",
     "time", "say time", "tell time",
     "dis temps", "combien temps", "quelle heure"): time_now,
    ("шутка", "расскажи шутку", "скажи шутку",
     "joke", "tell joke", "say joke",
     "blague", "dis blague", "raconte blague"): jokes,
    ("search","google",
     "найди"): browser_search,
    ("премьер", "включи премьер", "включи premier", "premier"): premier_search,
    ("погода", "покажи погоду",
     "weather", "show weather",
     "temps", "montre temps", "météo", "montre météo"): weather,
    ("определи пол", "пол", 
     "define gender", "gender", "define sex", "sex",
     "détermine sexe", "identifies sexe", "sexe"): sex_recognition,
    ("сменить язык", "поменять язык", "хочу сменить язык", "хочу поменять язык", "смена языка", "смени язык", "поменяй язык",
     "change language",
     "changer langue", "change langue"): change_language,
    ("no command"): no_command
}


def command_search(text):
    """
    Search for a command and transfer options for it
    :param text: input text
    :return: command with command options 
    """
    for key in commands.keys():
        for i in range(1,len(voice_input)+1):
            if " ".join(voice_input[:i]) in key:
                command = " ".join(voice_input[:i])
                command_options = [str(option) for option in voice_input[i:len(voice_input)]]
                return command, command_options
    return 'no command', ''
            


def command_definition(command_name: str, *args):
    """
    Executing a user-defined command and arguments
    :param command_name: command name
    :param args: arguments to be passed to the method
    :return: None
    """
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass  # print("Command not found")
            

if __name__ == '__main__': 
    
    voiceAssistance = voiceAssistance()
    voiceAssistance.name = 'alice'
    voiceAssistance.sex = 'female'
    voiceAssistance.language = 'ru'
    
    
    tts = pyttsx3.init()
    define_voice()
    default_volum_speed()
    tree = etree.parse("traduction.xml")
    translator = Translator()
    model = init_model()
    model.load_weights("data/model.h5")

    # Start of speech recording and command execution
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

            
            


        
    
    
    