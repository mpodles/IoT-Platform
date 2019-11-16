import logging
import socket
import sys
import time
from util import *

logger = logging.getLogger()


def main(host='192.168.1.12', port=1100):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    for i in range(2):
        sock.sendto(b'0', (host, port))



    data, addr = sock.recvfrom(1024)
    print('client received: {} {}'.format(addr, data))
    peerAddr = msg_to_addr(data)
    while True:
        sock.sendto(b'0', peerAddr)
        data, addr = sock.recvfrom(1024)
        print('client received: {} {}'.format(addr, data))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main()