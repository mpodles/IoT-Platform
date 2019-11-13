import logging
import socket
import sys
import time
from util import *

class Connector:
    def __init__(self):
        pass
    def connectDevice(self,device):
        pass
    def getDevices(self):
        pass
    @staticmethod
    def authenticate(login,password):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost',1101))
        sock.sendall(str.encode("login="+str(login)+" password="+str(password)))
        sock.recv(1024)
    def sendData(self):
        pass
    def readData(self):
        pass

