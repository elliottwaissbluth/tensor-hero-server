import pickle
import numpy as np

def getChart(audio_path):
    with open(audio_path, 'rb') as f:
        audio = pickle.load(f)
    (raw_audio, sr, title) = audio
    
    print(f'title in getChart: {title}')
    print(f'audio shape: {raw_audio.shape}')
    print(f'sr: {sr}')
