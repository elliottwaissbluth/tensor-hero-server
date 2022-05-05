import pickle
import numpy as np
from baseline import create_notes_array, generate_notes, onset_time, onset_time_bins, write_song_from_notes_array
import requests
import time

def getChart(audio_path, jobId):
    with open(audio_path, 'rb') as f:
        audio = pickle.load(f)
    (raw_audio, sr, title) = audio
    
    # FIXME: Source separation
    time.sleep(10)
    
    # FIXME: Spectrogram computation
    requests.post('http://app:5000/updateStatus',
                  json = {'status' : 1, 'jobId' : jobId})
    time.sleep(10)

    # FIXME: Flattening array computation
    requests.post('http://app:5000/updateStatus',
                  json = {'status' : 2, 'jobId' : jobId})
    time.sleep(10)

    # FIXME: Inference computation
    requests.post('http://app:5000/updateStatus',
                  json = {'status' : 3, 'jobId' : jobId})
    
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


    # FIXME: Flattening output
    requests.post('http://app:5000/updateStatus',
                  json = {'status' : 4, 'jobId' : jobId})
    time.sleep(10)

    # FIXME: Writing chart
    requests.post('http://app:5000/updateStatus',
                  json = {'status' : 5, 'jobId' : jobId})
    chart_string = write_song_from_notes_array(song_metadata, notes_array)
    time.sleep(10)

    return chart_string
