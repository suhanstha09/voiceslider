import pyaudio
import numpy as np
import tkinter as tk
import threading 

CHUNK = 1024          
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_VOLUME = 3000   