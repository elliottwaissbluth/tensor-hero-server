from flask import Flask, jsonify, request, Response, g
from worker import getChart
from redis import Redis
from rq import Queue
from rq.job import Job
import pickle
import librosa
import numpy as np

r = Redis(host='redis', port=6379) 
queue = Queue(connection=r)
app = Flask(__name__)

@app.put('/createJob')
def createJob():
    # Get title of song and audio file from request
    title = request.form.get('title')
    audio = request.files.get('audio')
   
    # Load raw audio into numpy array, get sample rate 
    raw_audio, sr = librosa.load(audio)

    # Serialize tuple (raw_audio, sr, title) as pickle file in volume
    audio_path = '/home/node/app/audio.pkl'
    with open(audio_path, 'wb') as f:
      pickle.dump((raw_audio, sr, title), f)

    # Pass audio path to getChart(), which will return the notes array
    job = queue.enqueue(getChart, args=(audio_path,))

    return jsonify({'test' : 'success'}), 200


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
