from crc import CRC
import textwrap

class Demodulator:

    _divisor: str
    _crc: CRC
    _crc_len: int
    _paddingChar: str
    
    def __init__(self, divisor: str = "101101011", crc_length:int = 8, paddingChar:str = '-') -> None:
        self._divisor = divisor
        self._crc = CRC(divisor)
        self._crc_len = crc_length
        self._paddingChar = paddingChar


    def demod(self, dataStream: str) -> str:
        data = dataStream
        if (not self._crc.verifyCrc(data)):
            print("CRC Failed")
            return ""
        data = data[:-self._crc_len]
        ascii_bin_array = textwrap.wrap(data, 8)
        ascii_dec_array = []
        padding = format(ord(self._paddingChar), '08b')
        for a in ascii_bin_array:
            if (a != padding):
                ascii_dec_array.append(int(a, 2))
        output = ""
        for b in ascii_dec_array:
            output += chr(b)
            print(f"{chr(b)} - {b}")
        return output


if __name__ == "__main__":
    demod = Demodulator()
    x = demod.demod("01110011001011010010110101110000")
    print(x)
