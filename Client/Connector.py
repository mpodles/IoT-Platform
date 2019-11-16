import logging
import socket
import sys
import time
from util import *
import multiprocessing as mp
import Client.Messenger as msg

global serverMessenger

def connectToServer(address='localhost',port=1101):
    global serverMessenger
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((address,port))
    except Exception as e:
        raise e
    print(sock)
    add=address+":"+str(port)
    serverMessenger = msg.Messenger(sock, add)
    #receiver = mp.Process(target=serverReceiver, args=(sock,))
    #sender = mp.Process(target=serverSender, args=(sock,))
    #receiver.start()
    #sender.start()

def connectToDevice(device):
    result=serverMessenger.askForConnectionToDevice(device)


def getDevices():
    result=serverMessenger.askForDevices()


def authenticate(login,password):
    result=serverMessenger.sendLoginRequest(login,password)
    #waitForResult()
    print (result)
    if result["response"]=="access_granted":
        return True
    else:
        return False

# def waitForResult():
#     while True:
#         print (serverMessenger.result)
#         time.sleep(1)
#         if serverMessenger.result["ID"]==serverMessenger.messageId:
#             break

# def serverReceiver(socket):
#     print("receiver started")
#     while True:
#         data = socket.recv(1024)
#         print(bytes.decode(data))

# def serverSender(socket):
#     print("sender started")
#     while True:
#         socket.sendall("elo".encode())
#         print("elo sent")
#         time.sleep(5)

