from scapy.all import *
from typing import List
import logging, time
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

class PacketSender():
    
    packet: UDP
    iface: str
    frags: List[str]
    count: int
    
    def __init__(self, dest: str="192.168.1.1", count: int = 5, iface: str = "en7") -> None:
        payload = b'U' * 1472
        self.iface = iface
        self.count = count
        self.packet = IP(dst = dest, proto=17)/UDP()/payload
        self.frags = fragment(self.packet)
    
    
    def sendPackets(self) -> None:
        # for f in self.frags:
        #     send(f, verbose = False, iface=self.iface)
        send(self.packet, count = self.count, verbose = False, iface = self.iface)
        # print("...")



if __name__ == "__main__":
    sender = PacketSender()
    print(sender.frags)
    # for i in range (50):
    #     sender.sendPackets()
    # print("Sending packets")
