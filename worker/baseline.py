import numpy as np
import librosa
import random

def onset_time(y, sr):
    '''
    Loads the song at song_path, computes onsets, returns array of times

    ~~~~ ARGUMENTS ~~~~
    - y (1D numpy array): raw audio
    - sr (int): sample rate
    
    ~~~~ RETURNS ~~~~
    - onset_times (1D numpy array): Array of times (in seconds) where onsets were detected in y
    '''
    # Load the songs and the notes arrays one at a time
    # for idx in range (len(song_paths)):
    # Load the song
    print(f'min y: {np.min(y)}')
    print(f'max y: {np.max(y)}')

    # resample the song if it isn't sr=22050 (for consistent sizing)
    if not sr == 22050:
        y = librosa.resample(y, sr, 22050)
        sr = 22050

    #source seperation, margin can be tuned 
    # y_harmonic, _ = librosa.effects.hpss(y, margin=2.0)

    # Set Hop_len
    hop_len = 512

    onset_frame_backtrack = librosa.onset.onset_detect(y, sr = sr, hop_length = hop_len, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frame_backtrack, hop_length=hop_len)

    return onset_times

def onset_time_bins(onset_times):
    otb = [int(x) for x in onset_times*100]
    return otb

def create_notes_array(onsets, notes):
    '''
    Takes equal length sequences of onsets and notes and creates a notes array which can be used to create
    final song output (leveraging Model_1/Processing/m1_postprocessing.py -> write_song_from_notes_array())

    ~~~~ ARGUMENTS ~~~~
    - onsets : list
        - contains onset times as 10ms bins
        - should be output of onset_time_bins()
    
    - notes : list or numpy array
        - notes corresponding to the onsets
    '''
    if type(notes) is np.ndarray:
        notes = notes.tolist()

    assert len(onsets) <= len(notes), 'ERROR: There are more onsets than notes'

    # Cut down notes if there are more notes than onsetse
    if len(notes) > len(onsets):
        notes = notes[:(len(onsets)-1)]
    
    notes_array = np.zeros(onsets[-1]+1)
    np.put(notes_array, onsets[:-1], notes)

    return notes_array
    
def generate_notes(onset, interval_length=100):
    '''
    Function that takes in onsets and generates notes based on the time interval difference
    User can change the interval
    Shorter intervals will be a scale, longer intervals will be chords
    Interval length: 100 equals 1 sec
    Output is same length as onset and a numpy array
    '''
    # Notes: 1-5 are single notes
    # 6 - 31 are chords
    # 32 is open note
    # conditions:
    # check onset and onset + 1
    # if < 2 then it should be single note
    curr_note = 0
    note_array = []
    # need to generate first note
    if onset[1] - onset[0] < interval_length:
        curr_note = random.randint(1,5)
        note_array.append(curr_note)
    else:
        curr_note = random.randint(6,31)
        note_array.append(curr_note)    
    
    
    for i in range(1,len(onset)-1): # since we'll be forward looking by one
        curr_note = calc_note(i,onset, curr_note)
        note_array.append(curr_note)

    # Looks at last note and compares will repeat 
    if (note_array[-1] < 6) :
        curr_note = random.randint(1,5)
        note_array.append(curr_note)
    else:
        curr_note = random.randint(6,31)
        note_array.append(curr_note)
   
    return note_array

def calc_note(idx, onset, curr_note, interval_length=100):
    # if short interval and current note is a single note
    n = random.random()
    
    # short and short = short - no change in state
    if (onset[idx] - onset[idx-1] < interval_length) & (onset[idx+1] - onset[idx] < interval_length): # changed conditional to or
        if n < (1/3): # note repeats
            curr_note = curr_note
        elif n < (2/3): # note goes up (unless current note is 5)
            if curr_note == 5:
                curr_note = curr_note - 1
            else:
                curr_note = curr_note + 1
        else: # note goes down (unless current note is 1)
            if curr_note == 1:
                curr_note = curr_note + 1
            else:
                curr_note = curr_note - 1
    
    # short and long = short - no change
    elif (onset[idx] - onset[idx-1] < interval_length) & (onset[idx+1] - onset[idx] > interval_length):
        if n < (1/3): # note repeats
            curr_note = random.randint(6,31)
        elif n < (2/3): # note goes up (unless current note is 5)
            if curr_note == 5:
                curr_note = curr_note - 1
            else:
                curr_note = curr_note + 1
        else: # note goes down (unless current note is 1)
            if curr_note == 1:
                curr_note = curr_note + 1
            else:
                curr_note = curr_note - 1
                
    # long and short = short - change 
    elif (onset[idx] - onset[idx-1] > interval_length) & (onset[idx+1] - onset[idx] < interval_length):
        curr_note = random.randint(1,5)
        
    # Long and Long = Long - no change
    else:
        curr_note = random.randint(6,31)
    return curr_note

def generate_centroid_notes(onset, centroid, interval_length=100):
    '''[summary]

    Args:
        onset ([type]): [description]
        centroid ([type]): [description]
        interval_length (int, optional): [description]. Defaults to 100.

    Returns:
        [type]: [description]
    '''
    # Notes: 1-5 are single notes
    # 6 - 31 are chords
    # 32 is open note
    # conditions:
    # check onset and onset + 1
    # if < 2 then it should be single note
    
    # centroid format is 10ms bins, each index corresponds to 10ms of time
    
    curr_note = 0
    note_array = []
    # need to generate first note
    if onset[1] - onset[0] < interval_length:
        curr_note = random.randint(1,5)
        note_array.append(curr_note)
    else:
        curr_note = random.randint(6,31)
        note_array.append(curr_note)    
    
    
    for i in range(1,len(onset)-1): # since we'll be forward looking by one
        curr_note = calc_note(i,onset, curr_note)
        note_array.append(curr_note)

    # Looks at last note and compares will repeat 
    if (note_array[-1] < 6) :
        curr_note = random.randint(1,5)
        note_array.append(curr_note)
    else:
        curr_note = random.randint(6,31)
        note_array.append(curr_note)
   
    return note_array

# ---------------------------------------------------------------------------- #
#                            song writing functions                            #
# ---------------------------------------------------------------------------- #

# Convert notes array to strings representing note events
# This is useful for writing .chart files from notes arrays
notes_to_chart_strings = {
    1 : ['0'],
    2 : ['1'],
    3 : ['2'],
    4 : ['3'], 
    5 : ['4'],
    6 : ['0','1'],
    7 : ['0','2'],
    8 : ['0','3'],
    9 : ['0','4'],
    10 : ['1','2'], 
    11 : ['1','3'],
    12 : ['1','4'],
    13 : ['2','3'],
    14 : ['2','4'],
    15 : ['3','4'],
    16 : ['0','1','2'],
    17 : ['0','1','3'],
    18 : ['0','1','4'],
    19 : ['0','2','3'],
    20 : ['0','2','4'],
    21 : ['0','3','4'],
    22 : ['1','2','3'],
    23 : ['1','2','4'],
    24 : ['1','3','4'],
    25 : ['2','3','4'],
    26 : ['0','1','2','3'],
    27 : ['0','1','2','4'],
    28 : ['0','1','3','4'],
    29 : ['0','2','3','4'],
    30 : ['1','2','3','4'],
    31 : ['0','1','2','3','4'],
    32 : ['7'],
    218 : ['7']
}

def write_song_from_notes_array(song_metadata, notes_array):
    '''
    Takes song_metadata as well as notes_array and writes notes.chart as string

    ~~~~ ARGUMENTS ~~~~
    - song_metadata : dict
        - populates [Song] portion of .chart file
    - notes_array : numpy array
        - array of notes with each element corresponding to a 10ms time bin
    
    ~~~~ RETURNS ~~~~
    - chart_string (str): multi-line string which is exactly a .chart file
    '''
    notes_array = list(notes_array.astype(int))
    chart_string = """""" 

    # populate '[Song]' portion of file
    chart_string += ('[Song]\n')
    chart_string += ('{\n')
    for k, v in song_metadata.items():
        if k in ['Name', 'Artist', 'Charter', 'Album', 'Year', 'Genre', 'MediaType', 'MusicStream']:
            chart_string += ('  ' + k + ' = "' + str(v) + '"\n')
        else:
            chart_string += ('  ' + k + ' = ' + str(v) + '\n')
    chart_string += ('}\n')

    # Populate '[SyncTrack]' portion of file, skip [Events]
    chart_string += ('[SyncTrack]\n{\n  0 = TS 1\n  0 = B 31250\n}\n[Events]\n{\n}\n')

    # Populate notes in '[ExpertSingle]'
    chart_string += ('[ExpertSingle]\n{\n')

    # Fill in notes from notes array
    for idx, note in enumerate(notes_array):
        if note == 0: # ignore no note is present
            continue
        for n in notes_to_chart_strings[note]:
            chart_string += ('  ' + str(idx) + ' = ' + 'N ' + n + ' 0\n')
    chart_string += ('}')
    
    return chart_string 
