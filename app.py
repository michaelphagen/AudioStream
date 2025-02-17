# This app creates a simple gui for audio parameters to pass to the create_app function.

from server import create_app
import pyaudio
import FreeSimpleGUI as sg
from threading import Thread
import socket
import qrcode
import os
import webbrowser

# INFO: Get the IP address of the server by attempting a connecton
# RTRN: IP - the IP address of the server
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't have to be reachable, just attempt connection
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# INFO: Generate a QR code for the server URL
# ARGS: link - the URL to generate the QR code for
# RTRN: path - the path to the generated QR code
def generate_qr_code(link):
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

# INFO: Check the sample rates supported by the selected device
# ARGS: deviceIndex - the index of the selected device from PyAudio's get_device_info_by_index
# RTRN: supportedRates - a list of supported (common) sample rates in hz
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
            
# INFO: Get the audio settings of the ADC devices
# RTRN: devicesList - a list of dictionaries containing:
#                       - name: the name of the device
#                       - index: the index of the device
#                       - channels: the number of channels the device supports
#                       - supportedSampleRates: a list of supported (common) sample rates in hz
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
            device['index']=info['index']
            device['channels']=info['maxInputChannels']
            if device not in devicesList:
                devicesList.append(device)
    return devicesList

# INFO: Run the server with the selected audio parameters
# ARGS: deviceIndex - the index of the selected device from PyAudio's get_device_info_by_index
#       channels - the number of channels to use
#       sampleRate - the sample rate to use in hz
#       bitDepth - the bit depth to use
#       chunkSize - the chunk size to use
#       port - the port to run the server on
# RTRN: None
def runServer(deviceIndex, channels, sampleRate, bitDepth, chunkSize, port):
    app = create_app(deviceIndex, channels, sampleRate, bitDepth, chunkSize)
    app.run(host='0.0.0.0', debug=False, threaded=True,port=port)

# INFO: Create the GUI to be displayed while the server is running
# ARGS: deviceIndex - the index of the selected device from PyAudio's get_device_info_by_index
#       channels - the number of channels to use
#       sampleRate - the sample rate to use in hz
#       bitDepth - the bit depth to use
#       chunkSize - the chunk size to use
# RTRN: None
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
    # Wait for the user to stop the server
    while True:
        event, values = window.read()
        if event == 'link':
            webbrowser.open(url)
        if event == sg.WIN_CLOSED or event == 'Stop Server':
            break
    window.close()

# INFO: Main function to get the audio settings and display the GUI
def main():
    # Get the list of devices
    devicesList = getAudioSettings()
    bitDepths = [16, 24, 32]
    # 24 bit not supported by Apple devices, so remove it if on Mac
    if 'Darwin' in os.uname():
        bitDepths.remove(24)
    # Create a list of devices to display in the GUI (id: name)
    devicesDisplay = []
    for i in range(len(devicesList)):
        devicesDisplay.append(str(devicesList[i]['index']) + ': ' + devicesList[i]['name'])
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
        # Start the server with the selected audio parameters
        if event == 'Submit':
            window.close()
            serverRunningUI(int(values['device'].split(':')[0]), int(values['channels']), int(values['sampleRate']), int(values['bitDepth']), int(values['chunkSize']))
        # Update the sample rate, bit depth, and channels lists when a new device is selected
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
        # Close the window if the user cancels or closes the window
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            # if QR code exists, delete it
            if os.path.exists("qr_code.png"):
                os.remove("qr_code.png")
            window.close()
            return None

# Run the main function if this file is run
if __name__ == '__main__':
    main()