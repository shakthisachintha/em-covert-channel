#region Libraries
import threading, time, queue
from modulator import Modulator, modulateMedium
from demodulator import Demodulator
import configparser
#endregion

#region Config Parsing
config = configparser.ConfigParser()
config.read('config.ini')
general_config = config['GENERAL']

modulationMedium = modulateMedium.physical if general_config['ModulationMedium'] == "Hardware" else modulateMedium.software
bitTime = int(general_config['BitTime'])
iface = general_config['NetworkInterface']
destination = general_config['Destination']
packetCount = int(general_config['PacketCount'])
preamble = general_config['Preamble']
crcDivisor = general_config['CRCDivisor']
interFrameDelay = int(general_config['InterFrameDelay'])
charsPerFrame = int(general_config['CharsPerFrame'])
#endregion

data_queue = queue.Queue()
modu = Modulator(medium = modulationMedium, preamble=preamble, divisor=crcDivisor, bitTimeMilis=bitTime)

def getData(numOfChars: int) -> str:
    qsize = data_queue._qsize()
    string = ""
    if (qsize >= numOfChars):
        for i in range(numOfChars):
            string += data_queue.get()
        return string
    elif (qsize > 0):
        for i in range(qsize):
            string += data_queue.get()
    return string


def dataAvail() -> bool:
    return not data_queue.empty()


# def getInput():
#     while True:
#         message = str(input("Enter Message to Encode: "))
#         for c in message:
#             data_queue.put(c)


def sendData():
    demod = Demodulator()
    modu = Modulator(medium = modulationMedium, preamble=preamble, divisor=crcDivisor, bitTimeMilis=bitTime, payloadSize=charsPerFrame)
    while(True):
        time.sleep(int(interFrameDelay/1000))
        try:
            if (data_queue.empty()):
                continue
            stream = getData(charsPerFrame)
            # modu.modulateToMedium(stream)
            frame = modu._prepareFrame(stream)
            print(frame)
    
            # demod.demod(frame)
        except:
            ascii = ord(' ')


def getInput():
    message = str(input("Enter Message to Encode: "))
    for c in message:
        data_queue.put(c)
    frames = []
    while(dataAvail()):
        stream = getData(charsPerFrame)
        modu.modulateToMedium(stream)
        frame = modu._prepareFrame(stream)
        frames.append(frame)


def sendPreamble():
    modu.sendPreambleCont()

# t2 = threading.Thread(target=getInput, args=()).start()

while True:
    getInput()
# sendPreamble()
# 1010101001100001011100110110010001011011
#101010100001111100001111001101110000110011011010010101010101010111111110001111