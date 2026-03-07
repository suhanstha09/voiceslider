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

vol_label = tk.Label(
    root, text="Volume: 0",
    bg="#1e1e2e", fg="#a0a0ff", font=("Arial", 12)
)
vol_label.pack(pady=10)

hint = tk.Label(
    root, text="Adjust MAX_VOLUME in code if slider feels off",
    bg="#1e1e2e", fg="#555577", font=("Arial", 9)
)
hint.pack()

def listen():
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)

            # Calculate RMS loudness from raw audio
            rms = int(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))

            # Map RMS → 0 to 100
            volume = min(int((rms / MAX_VOLUME) * 100), 100)

            # Safely update GUI from main thread
            root.after(0, update_slider, volume)

        except Exception as e:
            print("Audio error:", e)
            break
        
def update_slider(volume):
    slider.set(volume)
    vol_label.config(text=f"Volume: {volume}")