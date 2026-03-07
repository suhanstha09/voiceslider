import pyaudio
import numpy as np
import tkinter as tk
import threading 

CHUNK = 1024          
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_VOLUME = 3000   

p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)
