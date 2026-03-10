import pyaudio
import numpy as np
import tkinter as tk
import threading 

CHUNK = 1024          
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_VOLUME = 3000   

# Noise handling:
# - Start with a short calibration period to learn room noise.
# - Keep adapting noise floor slowly when the room is quiet.
# - Only pass signal above the floor + margin (noise gate).
CALIBRATION_FRAMES = 40
NOISE_MARGIN = 220
NOISE_ADAPT_ALPHA = 0.03
ATTACK_ALPHA = 0.40
RELEASE_ALPHA = 0.12

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
    root, text="Auto noise cancellation is enabled",
    bg="#1e1e2e", fg="#555577", font=("Arial", 9)
)
hint.pack()

noise_floor = 0.0
calibration_samples = []
smoothed_level = 0.0

def listen():
    global noise_floor, smoothed_level

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)

            # Calculate RMS loudness from raw audio
            rms = int(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))

            if len(calibration_samples) < CALIBRATION_FRAMES:
                calibration_samples.append(rms)
                noise_floor = float(np.mean(calibration_samples))
                root.after(0, update_slider, 0)
                continue

            # Continuously adapt to changing background noise while quiet.
            if rms <= noise_floor + NOISE_MARGIN:
                noise_floor = ((1.0 - NOISE_ADAPT_ALPHA) * noise_floor) + (NOISE_ADAPT_ALPHA * rms)

            # Remove estimated noise floor and gate low-level residuals.
            speech_level = max(0.0, rms - (noise_floor + NOISE_MARGIN))

            # Fast response when speaking (attack), slower decay when stopping (release).
            alpha = ATTACK_ALPHA if speech_level > smoothed_level else RELEASE_ALPHA
            smoothed_level = ((1.0 - alpha) * smoothed_level) + (alpha * speech_level)

            # Map cleaned signal → 0 to 100
            volume = min(int((smoothed_level / MAX_VOLUME) * 100), 100)

            # Safely update GUI from main thread
            root.after(0, update_slider, volume)

        except Exception as e:
            print("Audio error:", e)
            break
        
def update_slider(volume):
    slider.set(volume)
    vol_label.config(text=f"Volume: {volume}")
    
thread = threading.Thread(target=listen, daemon=True)
thread.start()

root.mainloop()

stream.stop_stream()
stream.close()
p.terminate()