import logging
import socket
import sys
import multiprocessing as mp
import time
from util import *
import Bridge.Setup as setup
import Bridge.Messenger as msg


if __name__ == '__main__':
    msg.connectToServer()
    msg.awaitForModules()
    msg.registerBridge()
    time.sleep(2)
    msg.registerBridge()
