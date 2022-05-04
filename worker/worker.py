import pickle
import numpy as np
from baseline import create_notes_array, generate_notes, onset_time, onset_time_bins, write_song_from_notes_array

def getChart(audio_path):
    with open(audio_path, 'rb') as f:
        audio = pickle.load(f)
    (raw_audio, sr, title) = audio
    
    # Compute onsets and convert them to notes_array indices (10ms time bins)
    onset_times = onset_time(raw_audio, sr)
    onset_indices = onset_time_bins(onset_times)

    # Get notes to populate onset times with
    dense_notes = generate_notes(onset_times[:-1], interval_length=50)

    # Populate notes array at onset_indices with dense_notes
    notes_array = create_notes_array(onset_indices[:-1], dense_notes)
    
    # Define song metadata
    song_metadata = {
        'Name' : title,
        'Artist' : 'Forrest', #FIXME, get from user
        'Charter' : 'Tensor Hero',
        'Offset' : 0,
        'Resolution' : 192,
        'Genre' : 'rock', #FIXME, get from user
        'MediaType' : 'cd',
        'MusicStream' : 'song.ogg' #FIXME, has to be the name of music file returned to user
    }
    
    chart_string = write_song_from_notes_array(song_metadata, notes_array)
    # print(f'title in getChart: {title}')
    # print(f'audio shape: {raw_audio.shape}')
    # print(f'sr: {sr}')
    return chart_string

if __name__ == '__main__':
    chart_string = getChart('/home/node/app/audio.pkl')
    print(chart_string)