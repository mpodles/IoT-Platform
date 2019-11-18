import logging
import socket
import sys
import time
from util import *
import multiprocessing as mp
from requests import get

import Client.Messenger as msg

global serverMessenger

global bridgeMessenger

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

def connectToDevice(device,behindNat):
    global bridgeMessenger
    global serverMessenger
    if behindNat:
        result=serverMessenger.askForConnectionToDevice(device,behindNat)
    else:
        global bridgeMessenger
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        myPublicIp=get('https://api.ipify.org').text
        sock.bind((myPublicIp,1102))
        result = serverMessenger.askForConnectionToDevice(device, behindNat)
        print(sock)
        add = address + ":" + str(port)
        serverMessenger = msg.Messenger(sock, add)


def getBridgesForUser(userID):
    result=serverMessenger.askForBridges(userID)
    bridges=result["response"]
    return bridges

def getDevicesForBridge(bridgeID):
    result=serverMessenger.askForBridgesDevices(bridgeID)
    devices=result["response"]
    return  devices


def authenticate(login,password):
    result=serverMessenger.sendLoginRequest(login,password)
    if result["response"]=="access_granted":
        return int(result["UserID"])
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

