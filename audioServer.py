#! /usr/bin/env python3

import pyaudio
import socket
import select

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
PORT = 4444

audio = pyaudio.PyAudio()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', PORT))
serverSocket.listen(5)


def callback(in_data, frame_count, time_info, status):
    for s in read_list[1:]:
        s.send(in_data)
    return None, pyaudio.paContinue


# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                    stream_callback=callback)
# stream.start_stream()

read_list = [serverSocket]
print("recording...")

try:
    while True:
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is serverSocket:
                (clientSocket, address) = serverSocket.accept()
                read_list.append(clientSocket)
                print("Connection from", address)
            else:
                data = s.recv(1024)
                if not data:
                    read_list.remove(s)
except KeyboardInterrupt:
    pass

print("finished recording")

serverSocket.close()
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
