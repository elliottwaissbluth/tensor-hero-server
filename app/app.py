from flask import Flask, jsonify, request, Response, g
from worker import print_title
from redis import Redis
from rq import Queue
from rq.job import Job
import pickle
import os
import sys

r = Redis(host='redis', port=6379) 
queue = Queue(connection=r)
app = Flask(__name__)

@app.put('/createJob')
def createJob():
    # Load from volume from worker
    title_path = '/home/node/app/title.pkl'

    title = request.form.get('title')
    sys.stdout.write('pickling title')
    sys.stdout.write(os.getcwd())

    with open(title_path, 'wb') as f:
      pickle.dump(title, f)

    _ = queue.enqueue(print_title, args=(title_path,))

    return jsonify({'test' : 'success'}), 200


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
