import logging
import socket
import sys
import time
from util import *

logger = logging.getLogger()


def main(host='217.96.150.120', port=1100):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    for i in range(20):
        sock.sendto(b'0', (host, port))


    while True:
        data, addr = sock.recvfrom(1024)
        print('client received: {} {}'.format(addr, data))
        addr = msg_to_addr(data)
        sock.sendto(b'0', addr)
        data, addr = sock.recvfrom(1024)
        print('client received: {} {}'.format(addr, data))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main()