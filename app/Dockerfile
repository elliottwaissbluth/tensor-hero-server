FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install build-essential -y && apt-get install libsndfile1-dev -y
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["python", "app.py"]