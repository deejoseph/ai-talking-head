from gtts import gTTS
import os
from config import AUDIO_PATH

def generate_audio(text):
    tts = gTTS(text=text, lang='zh')
    tts.save(AUDIO_PATH)
    print("Audio generated:", AUDIO_PATH)