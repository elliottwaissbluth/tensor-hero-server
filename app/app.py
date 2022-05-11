from flask import Flask, jsonify, request
import worker
from redis import Redis
from rq import Queue
import pickle
import librosa
import numpy as np
from threading import Lock
import uuid

r = Redis(host='redis', port=6379) 
queue = Queue(connection=r)
app = Flask(__name__)
app.config['tasks'] = {}
app.config['locker'] = Lock()
status_options = [
  'SEPARATION',
  'SPECTROGRAM',
  'FLATTEN_ARRAY',
  'FEED',
  'TRANSFORM',
  'CONVERT_TO_CHART',
  'COMPLETED'
]

@app.put('/createJob')
def createJob():
    jobId = uuid.uuid1().hex

    # Get title of song and audio file from request
    audio = request.files.get('audio')
    metadata = {
      'title': request.form.get('title', type=str),
      'artist': request.form.get('artist', type=str),
      'genre': request.form.get('genre', default='', type=str),
      'album': request.form.get('album', default='', type=str),
      'year': request.form.get('year', default='', type=str),
      'extension': audio.filename.rsplit('.', 1)[-1].lower(),
    }
   
    # Load raw audio into numpy array, get sample rate 
    raw_audio, sr = librosa.load(audio)

    # Serialize tuple (raw_audio, sr) as pickle file in volume
    audio_path = f'/home/node/app/{jobId}.pkl'
    with open(audio_path, 'wb') as f:
      pickle.dump((raw_audio, sr), f)

    # Pass audio path to getChart(), which will return the notes array
    task = queue.enqueue(worker.getChart, args=(metadata, audio_path, jobId), job_id=jobId)
    
    # Model statuses
    ''' 
    0. SEPARATION - source separation
    1. SPECTROGRAM - spectrogram computation
    2. FLATTEN_ARRAY - flatten array
    3. FEED - inference
    4. TRANSFORM - flatten output
    5. CONVERT_TO_CHART - convert to chart
    6. COMPLETED - completed
    '''

    status = {
      'task' : task,
      'model_status': 0,
    }
    app.config['tasks'][jobId] = status
    
    response = jsonify(jobId = jobId)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 201

@app.get('/getJobStatus')
def getJobStatus():
    # Get the jobId and current model status from the request
    jobId = request.args.get('jobId')

    # Ensure jobId is in the kes
    if jobId not in app.config['tasks']:
      return jsonify(error = "jobId not found"), 404 

    current_status = status_options[app.config['tasks'][jobId]['model_status']]
    
    # If the task has not yet completed, return current model status
    if not app.config['tasks'][jobId]['task'].result:
      return jsonify(status=current_status), 200
    else:
      response = jsonify(status=status_options[-1], chart=app.config['tasks'][jobId]['task'].result)
      del app.config['tasks'][jobId]
      return response, 200

@app.post('/updateJobStatus')
def updateJobStatus():
  '''Updates the status of the the model progress
  '''
  update = request.get_json()
  jobId = update['jobId']
  newStatus = update['status']
  
  app.config['locker'].acquire()
  app.config['tasks'][jobId]['model_status'] = newStatus 
  app.config['locker'].release() 

  return '', 200 


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=4000, debug=True)
