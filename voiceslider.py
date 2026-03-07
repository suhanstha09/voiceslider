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
root = tk.Tk()
root.title("Voice Volume Slider")
root.geometry("400x220")
root.configure(bg="#1e1e2e")


label = tk.Label(
    root, text="🎤 Speak to control volume",
    bg="#1e1e2e", fg="white", font=("Arial", 14)
)
label.pack(pady=20)

slider = tk.Scale(
    root, from_=0, to=100,
    orient=tk.HORIZONTAL, length=320,
    bg="#1e1e2e", fg="white",
    troughcolor="#444", activebackground="#7c3aed",
    highlightthickness=0, font=("Arial", 10)
)
slider.pack()