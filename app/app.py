import email
from flask import Flask, jsonify, request, Response, g
import json
# import librosa
import logging
from worker import analyze_audio
from redis import Redis
from rq import Queue
from rq.job import Job
import numpy as np

r = Redis(host='redis', port=6379) 
queue = Queue(connection=r)
app = Flask(__name__)

@app.put('/createJob')
def createJob():
    audio = request.files.get('audio')
    # save the file locally to volume
    # Load from volume from worker
    
    title = request.form.get('title')
    # raw_audio, sr = librosa.load(audio)
    raw_audio, sr = np.array([0, 1, 2, 3, 4]), 22050
    print(type(raw_audio))
    _ = queue.enqueue(analyze_audio, args=(audio, sr))
    
    return jsonify({'test' : 'success'}), 200


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
