# This app creates a simple gui for audio parameters to pass to the create_app function.

from server import create_app
import pyaudio
import PySimpleGUI as sg
from threading import Thread
import socket
import qrcode
import os
import webbrowser

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_qr_code(link):
    #Creating an instance of qrcode
    qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    file_name = "qr_code"+ ".png"
    path = os.path.join(os.getcwd(), file_name)
    img.save(path)
    return path

def checkSampleRates(deviceIndex):
    normalRates=[44100, 48000, 88200, 96000, 176400, 19200]
    supportedRates=[]
    audio = pyaudio.PyAudio()
    for i in range(len(normalRates)):
        try:
            if audio.is_format_supported(normalRates[i], input_device=deviceIndex, input_channels=1, input_format=pyaudio.paInt16):
                supportedRates.append(normalRates[i])
        except:
            pass
    return supportedRates
            

def getAudioSettings():
    devicesList=[]
    audio = pyaudio.PyAudio()
    # Write get
    for i in range(audio.get_device_count()):
        if audio.get_device_info_by_index(i)['maxInputChannels'] > 0 and audio.get_device_info_by_index(i)['hostApi'] == 0:
            device={}
            info=audio.get_device_info_by_index(i)
            device['supportedSampleRates']=checkSampleRates(i)
            device['name']=info['name']
            device['index']=i
            device['channels']=info['maxInputChannels']
            # If device isn't already in the list, add it
            if device not in devicesList:
                devicesList.append(device)
    return devicesList

def runServer(deviceIndex, channels, sampleRate, bitDepth, chunkSize, port):
    app = create_app(deviceIndex, channels, sampleRate, bitDepth, chunkSize)
    app.run(host='0.0.0.0', debug=False, threaded=True,port=port)

def serverRunningUI(deviceIndex, channels, sampleRate, bitDepth, chunkSize):
    port=5000
    ip=get_ip()
    url="http://"+ip+":"+str(port)
    path=generate_qr_code(url)
    layout = [[sg.Text('Server Running')],[sg.Image(path)],[sg.Text('Scan QR code to connect')],[sg.Text('or go to: ')],[sg.Text(url,enable_events=True, key="link", font=(None, 12, "underline"),text_color='blue')],[sg.Button('Stop Server')]]
    window = sg.Window('Server Running', layout)
    server = Thread(target=runServer, args=(deviceIndex, channels, sampleRate, bitDepth, chunkSize, port))
    server.setDaemon(True)
    server.start()
    
    while True:
        event, values = window.read()
        if event == 'link':
            webbrowser.open(url)
        if event == sg.WIN_CLOSED or event == 'Stop Server':
            break
    window.close()

def main():
    # Get the list of devices
    devicesList = getAudioSettings()
    bitDepths = [16, 24, 32]
    # Create a list of devices to display in the GUI (id: name)
    devicesDisplay = []
    for i in range(len(devicesList)):
        devicesDisplay.append(str(i) + ': ' + devicesList[i]['name'])
    # Draw the GUI
    layout = [[sg.Text('Audio Settings')],
                [sg.Text('Device', size=(15, 1)), sg.Combo(devicesDisplay, size=(30, 1), key="device",enable_events=True)],
                [sg.Text('Sample Rate', size=(15, 1)), sg.Combo([], size=(30, 1), key="sampleRate",enable_events=True)],
                [sg.Text('Bit Depth', size=(15, 1)), sg.Combo([], size=(30, 1), key="bitDepth",enable_events=True)],
                [sg.Text('Channels', size=(15, 1)), sg.Combo([], size=(30, 1), key="channels",enable_events=True)],
                [sg.Text('Chunk Size', size=(15, 1)), sg.InputText('1024',size=(10, 1), key="chunkSize")],
                [sg.Submit(), sg.Cancel()]]
    window = sg.Window('Audio Settings', layout)
    while True:
        event, values = window.read()
        if event == 'Submit':
            window.close()
            serverRunningUI(int(values['device'].split(':')[0]), int(values['channels']), int(values['sampleRate']), int(values['bitDepth']), int(values['chunkSize']))
        if event == 'device':
            newDeviceIndex = int(values['device'].split(':')[0])
            newDeviceSampleRates = devicesList[newDeviceIndex]['supportedSampleRates']
            newDeviceMaxChannels = devicesList[newDeviceIndex]['channels']
            previousSampleRate = values['sampleRate']
            previousBitDepth = values['bitDepth']
            previousChannels = values['channels']
            # Update the sample rate list and select the previous sample rate if it is still supported
            window['sampleRate'].update(values=newDeviceSampleRates)
            if previousSampleRate in newDeviceSampleRates:
                window['sampleRate'].update(value=previousSampleRate)
            else:
                window['sampleRate'].update(value=newDeviceSampleRates[0])
            # Update the bit depth list and select the previous bit depth if it is still supported
            window['bitDepth'].update(values=bitDepths)
            if previousBitDepth in bitDepths:
                window['bitDepth'].update(value=previousBitDepth)
            else:
                window['bitDepth'].update(value=bitDepths[0])
            # Update the channels list and select the previous channels if it is still supported
            window['channels'].update(values=list(range(1,newDeviceMaxChannels+1)))
            if previousChannels in list(range(1,newDeviceMaxChannels+1)):
                window['channels'].update(value=previousChannels)
            else:
                window['channels'].update(value=1)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            # if QR code file exists, delete it
            if os.path.exists("qr_code.png"):
                os.remove("qr_code.png")
            window.close()
            return None


if __name__ == '__main__':
    main()