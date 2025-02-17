import numpy as np
from flask import Flask, Response
import pyaudio

# INFO: Create the Flask app
# ARGS: deviceIndex - the index of the selected device from PyAudio's get_device_info_by_index
#       channels - the number of channels to use
#       sampleRate - the sample sampleRate to use in hz
#       bitDepth - the bit depth to use
#       chunkSize - the chunk size to use
# RTRN: app - starts the Flask app
def create_app(deviceIndex, channels, sampleRate, bitDepth, chunkSize):
    app = Flask(__name__)
    audioInput = pyaudio.PyAudio()

    # Get format from bit depth
    if bitDepth == 16:
        FORMAT = pyaudio.paInt16
    elif bitDepth == 24:
        FORMAT = pyaudio.paInt24
    elif bitDepth == 32:
        FORMAT = pyaudio.paFloat32

    # INFO: Generate the header for the wav file
    # ARGS: sampleRate - the sample sampleRate to use in hz
    #       bitDepth - the bit depth to use
    #       channels - the number of channels to use
    # RTRN: header - the header for the wav file
    def genHeader(sampleRate, bitDepth, channels):
        datasize = 2000*10**6
        header = bytes("RIFF",'ascii')
        header += (datasize + 36).to_bytes(4,'little')
        header += bytes("WAVE",'ascii')
        header += bytes("fmt ",'ascii')
        header += (16).to_bytes(4,'little')
        header += (1).to_bytes(2,'little')
        header += (channels).to_bytes(2,'little')
        header += (sampleRate).to_bytes(4,'little')
        header += (sampleRate * channels * bitDepth // 8).to_bytes(4,'little')
        header += (channels * bitDepth // 8).to_bytes(2,'little')
        header += (bitDepth).to_bytes(2,'little')
        header += bytes("data",'ascii')
        header += (datasize).to_bytes(4,'little')
        return header

    # INFO: Create the audio route
    # RTRN: Response - the audio data from the buffer
    @app.route('/audio')
    def audio():
        # start Recording
        def sound():
            header = genHeader(sampleRate, bitDepth, channels)
            stream = audioInput.open(format=FORMAT, channels=channels,rate=sampleRate, input=True, input_device_index=deviceIndex,frames_per_buffer=chunkSize)
            yield(header)
            # INFO: Continuously read the audio stream and yield the data
            while True:
                buffer = stream.read(chunkSize,exception_on_overflow = False)
                yield(buffer)
        return Response(sound())

    # INFO: Create the client side webpage hosting the media player
    # RTRN: html - the html for the index page
    @app.route('/')
    def index():
        html="""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
                    <title>AudioStream</title>
                </head>
                <body>
                    <h1>Click play on the audio object below</h1>
                    <audio controls preload="none">
                        <source src="/audio" type="audio/x-wav;codec=pcm">
                        Your browser does not support the audio element.
                    </audio>
                    <br/>
                    AudioStream is developed and maintained by Michael Hagen
                    <br />
                    See the <a href="https://github.com/michaelphagen/AudioStream" target="_blank">GitHub</a> page for more information
                </body>
                </html>"""
        return html
    
    return app