# AudioStream

Stream an Audio Device to a webpage with Python

## How it works

AudioStream uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) to create a web server that streams audio from the selected audio device. The PCM audio is captured using [PyAudio](https://pypi.org/project/PyAudio/) and embedded into a webpage as an audio element. The webpage is served using Flask and can be accessed by any device on the same network. The app also displays a QR code that can be scanned to quickly access the webpage on a mobile device.

## How to use

### Windows

1. Download the [latest release](https://github.com/michaelphagen/AudioStream/releases) from GitHub
2. Run the executable
3. Select the audio device and parameters you want to use
4. Click "Confirm"
5. Go to the URL displayed on screen to listen to the audio.

### MacOS & Linux

1. Clone the repository with `git clone https://github.com/michaelphagen/AudioStream.git` or [download the zip](https://github.com/michaelphagen/AudioStream/archive/refs/heads/main.zip)
2. Install dependencies by double clicking the `mac_setup.command` file
3. Run the application with `python app.py`
4. Select the audio device and parameters you want to use
5. Click "Confirm"
6. Go to the URL displayed on screen to listen to the audio

## Dependencies

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [PyAudio](https://pypi.org/project/PyAudio/)
- [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)
- [qrcode](https://pypi.org/project/qrcode/)
- [PortAudio](http://www.portaudio.com/)
- [python-tk](https://wiki.python.org/moin/TkInter)

## Donate

If you find this project useful and you would like to donate toward on-going development you can use the link below. Any and all donations are much appreciated!
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/michaelphagen)