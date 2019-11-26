import logging
import socket
import sys
import threading as thr
import time
from util import *
import Bridge.Setup as setup
import Bridge.Messenger as msg


if __name__ == '__main__':
   # msg.connectToServer()
    modulesThread = thr.Thread(target=msg.awaitForModules)
    modulesThread.start()
    #msg.registerBridge()
    #time.sleep(2)
    #msg.registerBridge()
