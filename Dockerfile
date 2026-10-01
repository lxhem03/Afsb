FROM python:3.12-slim
WORKDIR /app

# ffmpeg provides ffprobe, used to read audio/subtitle track languages
# for auto-upload captions.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
