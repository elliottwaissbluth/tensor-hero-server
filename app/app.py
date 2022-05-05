from flask import Flask, jsonify, request
from flask import current_app
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
status_options = ['SEPARARATING', 'SPECTROGRAM', 'FLATTEN_ARRAY', 'INFERENCE', 'FLATTEN_OUTPUT', 'CHART_CONVERTING', 'COMPLETED']

@app.put('/createJob')
def createJob():
    # Get title of song and audio file from request
    title = request.form.get('title')
    audio = request.files.get('audio')
    
    #TODO: Extract extension from audio
    extension = '.ogg'
   
    # Load raw audio into numpy array, get sample rate 
    raw_audio, sr = librosa.load(audio)

    # Serialize tuple (raw_audio, sr, title) as pickle file in volume
    audio_path = '/home/node/app/audio.pkl'
    with open(audio_path, 'wb') as f:
      pickle.dump((raw_audio, sr, title), f)

    # Pass audio path to getChart(), which will return the notes array
    jobId = uuid.uuid1().hex
    task = queue.enqueue(worker.getChart, args=(audio_path, jobId), job_id=jobId)
    
    # Model statuses
    ''' 
    1. SEPARATING - source separation
    2. SPECTROGRAM - spectrogram computation
    3. FLATTEN_ARRAY - flatten array
    4. INFERENCE - inference
    5. FLATTEN_OUTPUT - flatten output
    6. CHART_CONVERTING - convert to chart
    '''

    status = {
      'task' : task,
      'model_status': 0,
    }
    app.config['tasks'][jobId] = status
    
    # # Wait for task to finish
    # while not task.result:
      # current_app.logger.debug('Waiting for task')
      # time.sleep(1)

    # if task:
        # response_object = {
            # "status": "success",
            # "data": {
                # "task_id": task.get_id(),
                # "task_status": task.get_status(),
                # "task_result": task.result,
            # },
        # }
    # else:
        # response_object = {"status": "error"}
    # current_app.logger.debug(f'chart_string: {task.result}')
    # return jsonify(response_object), 200
    response = jsonify(jobId = jobId)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 201

@app.get('/getStatus')
def getStatus():
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

@app.post('/updateStatus')
def updateStatus():
  '''Updates the status of the the model progress
  '''
  current_app.logger.debug('before update:')
  current_app.logger.debug(app.config['tasks'])

  update = request.get_json()
  jobId = update['jobId']
  newStatus = update['status']
  
  app.config['locker'].acquire()
  app.config['tasks'][jobId]['model_status'] = newStatus 
  app.config['locker'].release() 

  current_app.logger.debug('after update:')
  current_app.logger.debug(app.config['tasks'])
  
  return "", 200 


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
