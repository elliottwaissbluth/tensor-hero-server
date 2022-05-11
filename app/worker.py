import pickle
import numpy as np
from baseline import create_notes_array, generate_notes, onset_time, onset_time_bins, write_song_from_notes_array
import requests
import time

def getChart(metadata, audio_path, jobId):
    COM_ENDPOINT = 'http://ml-server:4000/updateJobStatus'

    with open(audio_path, 'rb') as f:
        audio = pickle.load(f)
    (raw_audio, sr) = audio
    
    # FIXME: Source separation
    time.sleep(8)
    
    # FIXME: Spectrogram computation
    requests.post(COM_ENDPOINT, json = {'status' : 1, 'jobId' : jobId})
    time.sleep(12)

    # FIXME: Flattening array computation
    requests.post(COM_ENDPOINT, json = {'status' : 2, 'jobId' : jobId})
    time.sleep(6)

    # FIXME: Inference computation
    requests.post(COM_ENDPOINT, json = {'status' : 3, 'jobId' : jobId})
    time.sleep(16)
    
    # Compute onsets and convert them to notes_array indices (10ms time bins)
    onset_times = onset_time(raw_audio, sr)
    onset_indices = onset_time_bins(onset_times)

    # Get notes to populate onset times with
    dense_notes = generate_notes(onset_times[:-1], interval_length=50)

    # Populate notes array at onset_indices with dense_notes
    notes_array = create_notes_array(onset_indices[:-1], dense_notes)
    
    # Define song metadata
    song_metadata = {
        'Name' : metadata['title'],
        'Artist' : metadata['artist'],
        'Charter' : 'Tensor Hero',
        'Offset' : 0,
        'Resolution' : 192,
        'MediaType' : 'cd',
        'MusicStream' : 'song.{}'.format(metadata['extension']),
    }
    if len(metadata['album']) > 0:
        song_metadata['Album'] = metadata['album']
    if len(metadata['genre']) > 0:
        song_metadata['Genre'] = metadata['genre']
    if len(metadata['year']) > 0:
        song_metadata['Year'] = ', {}'.format(metadata['year'])


    # FIXME: Flattening output
    requests.post(COM_ENDPOINT, json = {'status' : 4, 'jobId' : jobId})
    time.sleep(6)

    # FIXME: Writing chart
    requests.post(COM_ENDPOINT, json = {'status' : 5, 'jobId' : jobId})
    chart_string = write_song_from_notes_array(song_metadata, notes_array)
    time.sleep(6)

    return chart_string
