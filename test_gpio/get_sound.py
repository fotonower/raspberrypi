import sounddevice as sd
import numpy as np

fs = 44100
sd.default.device = 'USB Audio Device'

duration = 10.5  # seconds
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)

#myrecording = sd.rec(int(duration * fs))
sd.wait()