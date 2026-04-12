import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

AUDIO_PATH = os.path.join(INPUT_DIR, "audio.wav")
IMAGE_PATH = os.path.join(INPUT_DIR, "face.png")

SADTALKER_PATH = os.path.join(BASE_DIR, "sadtalker")