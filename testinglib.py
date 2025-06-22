import sounddevice as sd
import numpy as np
from flask import Flask
import psutil
import threading  # Added missing import

print("Testing audio system...")
duration = 1.5  # seconds
fs = 44100
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print("Audio test successful!")

print("Testing resource monitoring...")
print(f"CPU: {psutil.cpu_percent()}% | Memory: {psutil.virtual_memory().percent}%")

print("Testing web server...")
app = Flask(__name__)
@app.route('/')
def test(): return "OK"

# Start Flask in a separate thread
threading.Thread(target=app.run, kwargs={'port': 5000}).start()
print("Web server started on http://localhost:5000")
