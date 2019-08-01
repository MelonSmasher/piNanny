FROM balenalib/armv7hf-debian-python:3-buster

ENV PyAudio_PY_VERSION=0.2.11

WORKDIR /usr/src/app

COPY audioServer.py audioServer.py
COPY entrypoint.sh entrypoint.sh

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y build-essential python3 python3-dev portaudio19-dev alsa-tools alsa-utils && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir --trusted-host pypi.python.org PyAudio==${PyAudio_PY_VERSION}

CMD ["./entrypoint.sh"]