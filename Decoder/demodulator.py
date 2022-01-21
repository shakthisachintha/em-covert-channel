import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import math
import configparser
from typing import List
from hammingCode import Hamming
from decoder import Decoder

#region Config Parsing
config = configparser.ConfigParser()
config.read('config.ini')
general_config = config['GENERAL']

bitTime = int(general_config['BitTime'])
crcLength = int(general_config['CRCLength'])
crcDivisor = general_config['CRCDivisor']
paddingChar = general_config['PaddingCharacter']
sampleRate = int(float(general_config['SampleRate']))
windowSize = int(general_config['WindowSize'])

#endregion

windowsPerBit = (bitTime/1000) * sampleRate / windowSize
windowsPerBit = math.ceil(windowsPerBit)


# Uses scipy library
def computeNormalizedXcor(a, b):
    normalized_a = (a - np.mean(a)) / (np.std(a))
    normalized_b = (b - np.mean(b)) / (np.std(b))
    c = signal.correlate(normalized_a, normalized_b,
                         mode="full") / max(len(a), len(b))
    center = int(len(c)/2)
    return (c[center], center, c)

class Demodulator:

    def __init__(self, preambleThres: float = 0.05, bitThres: float = 0.03):
        self._sampleBinPreamble = np.fromfile(open("./binPreamble.bin"), dtype=np.float64)
        self._sampleBinOne = np.fromfile(open("./BinOne.bin"), dtype=np.float64)
        self._sampleBinZero = np.fromfile(open("./BinZero.bin"), dtype=np.float64)
        self._preambleThres = preambleThres 
        self._bitThres = bitThres

    
    def setBitThreshold(self, bitThres: float = 0.03) -> None:
        self._bitThres = bitThres

    
    def setBitThreshold(self, preambleThres: float = 0.05) -> None:
        self._preambleThres = preambleThres
    
    
    def _computeNormalizedXcor(self, a, b):
        normalized_a = (a - np.mean(a)) / (np.std(a))
        normalized_b = (b - np.mean(b)) / (np.std(b))
        c = signal.correlate(normalized_a, normalized_b,
                             mode="full") / max(len(a), len(b))
        center = int(len(c)/2)
        return (c[center], center, c)

    
    def _correctErrors(self, demodulatedFrame: List[int]) -> str:
        frame = demodulatedFrame
        chunk_size = 7
        ham = Hamming()
        dec = ""
        for i in range(0, len(frame), chunk_size):
            chunk = frame[i:i+chunk_size]
            input_vector = np.matrix(chunk).transpose()
            corrected = ham.getOriginalMessage(input_vector)[0]
            x = ""
            for i in corrected:
                x += str(i)
            dec += x
        return dec

    
    def _decodeFrame(self, correctedFrame: str) -> str:
        decod = Decoder(divisor=crcDivisor, crc_length=crcLength, paddingChar=paddingChar)
        m = decod.decode(correctedFrame)
        return m

    
    def demodulateSignal(self, data: List[float], statusChange=None, decodedFrame=None) -> List[List[int]]:
        preambleThres = self._preambleThres
        bitThres = self._bitThres

        blockStart = 0
        samples = []
        enabled = False
        preambleLength = 8
        crcLength = 8
        payloadLength = 56
        numOfBitsToDecode = payloadLength
        allDecodedFrames = []
        decoded = []
        bitsDecoded = 0
        framesDecoded = 0
        statusChange("Detecting Preamble")
        while blockStart < len(data):
            window = data[blockStart: (blockStart + windowSize)]
            blockStart += windowSize
            samples.append(window)

            # Detect Preamble
            if not enabled:
                if len(samples) >= (preambleLength * windowsPerBit):
                    preamble = [
                        item for sublist in samples[:preambleLength*windowsPerBit] for item in sublist]
                    comp = self._computeNormalizedXcor(preamble, self._sampleBinPreamble)
                    samples.pop(0)
                    if (comp[0] >= preambleThres):
                        enabled = True
                        print("\nPreamble Detected")
                        statusChange("Preamble Detected")
                        # procedure to calculate the optimal threshold
                        samples = []

            # Once the preamble is deteced decodes each bits
            if enabled and len(samples) >= windowsPerBit:
                bit = [item for sublist in samples[:windowsPerBit]
                       for item in sublist]
                compOne = self._computeNormalizedXcor(self._sampleBinOne, np.array(bit))
                compZero = self._computeNormalizedXcor(self._sampleBinZero, np.array(bit))
                if compZero[0] > bitThres:
                    decoded.append(0)
                if compOne[0] > bitThres:
                    decoded.append(1)
                isDecoded = True if compOne[0] > bitThres or compZero[0] > bitThres else False
                if isDecoded:
                    bitsDecoded += 1
                    for r in range(windowsPerBit):
                        samples.pop(0)
                else:
                    samples.pop(0)

                print(bitsDecoded, end=" ")
                if bitsDecoded >= numOfBitsToDecode:
                    enabled = False
                    samples = []
                    bitsDecoded = 0
                    allDecodedFrames.append(decoded)
                    framesDecoded += 1
                    corrected = self._correctErrors(decoded)
                    message = self._decodeFrame(corrected)
                    print(message)
                    decodedFrame(message)
                    statusChange("Detecting Preamble")
                    decoded = []
        statusChange("Decoding Finished")
        return allDecodedFrames


def eventHandler(x):
    print(x)

if __name__ == "__main__":
    data = list(np.fromfile(open("./generatedTestSignal.bin"), dtype=np.float64))
    demod = Demodulator()
    dec = demod.demodulateSignal(data, eventHandler, eventHandler)
    print(dec)
    # x = ['01110011011010000110000110001010', '01101011011101000110100010110100', '01101001001000000111001101000001',
    #      '01100001011000110110100010011111', '01101001011011100111010010100111', '01101000011000010010110111010100']
    # for c in decodedMessages: print(c, end="")
    # print(x)
