#region Libraries
from crc import CRC
import enum
import time
from packetSender import PacketSender
from demodulator import Demodulator
import configparser
from hammingCode import Hamming
#endregion

#region Config Parsing
config = configparser.ConfigParser()
config.read('config.ini')
general_config = config['GENERAL']

iface = general_config['NetworkInterface']
destination = general_config['Destination']
packetCount = int(general_config['PacketCount'])
paddingChar = general_config['paddingCharacter']
#endregion

'''
frame structure
preamble - 8 bit
data - 32 bit
crc - 8 bit 
'''

def getCurrentTimeMillis() -> int:
    ms = time.time_ns() // 1_000_000
    return ms

def getAsciiStringFromChar(char: str) -> str:
    x = format(ord(char), '08b')
    return x

class modulateMedium(enum.Enum):
    physical = 1
    software = 2

class Modulator:
    
    _preamble: str
    _divisor: str
    _payloadSize: int
    _medium: modulateMedium
    _sender: PacketSender
    _bitTimeMilis: int
    
    
    def __init__(self, medium: modulateMedium = modulateMedium.software,
     preamble: str = "10101010", divisor: str="101101011", payloadSize = 4, bitTimeMilis:int = 200) -> None:
        self._divisor = divisor
        self._preamble = preamble
        self._medium = medium
        self._bitTimeMilis = bitTimeMilis
        self._payloadSize = payloadSize
        self._sender = PacketSender(count=packetCount, iface=iface, dest=destination)

    
    def _calcCRC(self, dataString: str)-> str:
        c = CRC(self._divisor)
        crc = c.calculateCrc(dataString)
        return crc

    
    def _prepareFrame(self, charStream: str)-> str:
        ''' 
        Add padding to data if necessary, add preamble
        calculate CRC and return the binary string
        '''
        ham = Hamming()
        ascii_binary_stream = ""
        for char in charStream:
            asc = getAsciiStringFromChar(char)
            ascii_binary_stream += asc
        if (len(charStream) < self._payloadSize):
            pad_len = self._payloadSize - len(charStream)
            for i in range(pad_len):
                # print("padding = ", paddingChar)
                ascii_binary_stream += format(ord(paddingChar), '08b')

        crc = self._calcCRC(ascii_binary_stream)
        ascii_binary_stream = ascii_binary_stream + crc
        
        hamCode = ""
        for i in range(0, len(ascii_binary_stream), 4):
            segment = ascii_binary_stream[i: i+4]
            enc = ham.encode(segment)
            enc = ham.matrixToString(enc)
            hamCode += enc
        finalString = self._preamble + hamCode
        return finalString
    

    def modulateToMedium(self, dataString: str) -> None:
        frame = self._prepareFrame(dataString)
        if (self._medium == modulateMedium.software):
            for bit in frame:
                print(bit, end = "")
        elif (self._medium == modulateMedium.physical):
                self._manchestorModulate(frame)


    def _manchestorModulate(self, bitStream: str) -> None:
        bitEndTime = getCurrentTimeMillis()
        print(bitStream)
        bitTimeMillis = self._bitTimeMilis
        for bit in bitStream:
            bitEndTime +=  bitTimeMillis
            halfBitEndTime = bitEndTime - (bitTimeMillis/2)
            if bit == "1":
                print(f"Sending 1")
                time.sleep((bitTimeMillis / 2)/1000)
                while (getCurrentTimeMillis() < bitEndTime):
                    self._sender.sendPackets()
                    pass
            if bit == "0":
                print(f"Sending 0")
                while getCurrentTimeMillis() < halfBitEndTime:
                    self._sender.sendPackets()
                    pass
                time.sleep((bitTimeMillis/2)/1000)
        print("Frame Sent")

    def sendPreambleCont(self) -> None:
        bitEndTime = getCurrentTimeMillis()
        bitTimeMillis = self._bitTimeMilis
        bit = "1"
        while True:
            bitEndTime +=  bitTimeMillis
            halfBitEndTime = bitEndTime - (bitTimeMillis/2)
            if bit == "1":
                print(f"Sending 1")
                time.sleep((bitTimeMillis / 2)/1000)
                while (getCurrentTimeMillis() < bitEndTime):
                    self._sender.sendPackets()
                    # pass
            if bit == "0":
                print(f"Sending 0")
                while getCurrentTimeMillis() < halfBitEndTime:
                    self._sender.sendPackets()
                    # pass
            bit = "0" if bit == "1" else "1"
            time.sleep((bitTimeMillis/2)/1000)
# 1010101000011111000011110011011100001100110110100111100001011010