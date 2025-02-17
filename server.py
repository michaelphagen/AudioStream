from flask import Flask, Response,render_template
import pyaudio

def create_app(DEVICEINDEX, CHANNELS, RATE, BITDEPTH, CHUNK):

    print("Starting Stream for Device: " + str(DEVICEINDEX) + " with Sample Rate: " + str(RATE) + " and Bit Depth: " + str(BITDEPTH) + " and Chunk Size: " + str(CHUNK) + " and Channels: " + str(CHANNELS))
    app = Flask(__name__)
    audio1 = pyaudio.PyAudio()

    # Get format from bit depth
    if BITDEPTH == 16:
        FORMAT = pyaudio.paInt16
    elif BITDEPTH == 24:
        FORMAT = pyaudio.paInt24
    elif BITDEPTH == 32:
        FORMAT = pyaudio.paInt32

    def genHeader(sampleRate, bitsPerSample, channels):
        datasize = 2000*10**6
        o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE",'ascii')                                              # (4byte) File type
        o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
        o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
        o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
        o += (channels).to_bytes(2,'little')                                    # (2byte)
        o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
        o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
        o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
        o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
        o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
        o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
        return o

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