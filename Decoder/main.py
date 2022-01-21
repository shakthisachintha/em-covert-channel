from demodulator import Demodulator
import numpy as np

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
