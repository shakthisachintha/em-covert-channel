def _xor(a, b) -> str:
    # initialize result
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
 
    return ''.join(result)


class CRC:
    _divisor:str
    
    def __init__(self, divisor: str) -> None:
        self._divisor = divisor

    
    def calculateCrc(self, dataString: str) -> str:
        return self._div(dataString + '0'*(len(self._divisor) - 1))

    
    def verifyCrc(self, bString: str) -> bool:
        '''bString: data string along with the crc'''
        rem = self._div(bString)
        return True if rem == '0'*(len(self._divisor) - 1) else False

    
    def _div(self, divident: str) -> str:
        # Number of bits to be XORed at a time.
        
        pick = len(self._divisor)
    
        # Slicing the divident to appropriate
        # length for particular step
        tmp = divident[0 : pick]
    
        while pick < len(divident):
        
            if tmp[0] == '1':
            
                # replace the divident by the result
                # of XOR and pull 1 bit down
                tmp = _xor(self._divisor, tmp) + divident[pick]
    
            else: # If leftmost bit is '0'
            
                # If the leftmost bit of the dividend (or the
                # part used in each step) is 0, the step cannot
                # use the regular self._divisor; we need to use an
                # all-0s self._divisor.
                tmp = _xor('0'*pick, tmp) + divident[pick]
    
            # increment pick to move further
            pick += 1
    
        # For the last n bits, we have to carry it out
        # normally as increased value of pick will cause
        # Index Out of Bounds.
        if tmp[0] == '1':
            tmp = _xor(self._divisor, tmp)
        else:
            tmp = _xor('0'*pick, tmp)
    
        checkword = tmp
        return checkword

if __name__ == "__main__":
    c = CRC("10101")
    b = c.calculateCrc("110100")
    print(b)
    print(c.verifyCrc("1101001101"))