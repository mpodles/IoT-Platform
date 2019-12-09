import logging
import socket
import sys
import threading as thr
import time
import Setup as setup
import Messenger as msg


if __name__ == '__main__':
    ipAdd="192.168.1.17"
    msg.connectToServer(ipAdd)
    msg.registerBridge()
    modulesThread = thr.Thread(target=msg.awaitForModules)
    modulesThread.start()
