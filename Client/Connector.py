import logging
import socket
import sys
import time
from util import *
import multiprocessing as mp
import threading as thr
from requests import get

import Client.Messenger as msg

global serverMessenger

global bridgeMessenger

global tcpSocket

global udpSocket

global seenAs

def connectToServer(address='localhost',port=1101):
    global serverMessenger
    global seenAs
    global tcpSocket
    global udpSocket
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.connect((address,port))
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seenAs=bytes.decode(tcpSocket.recv(1024))
    print("I'm seen as tcp: ",seenAs)
    serverMessenger = msg.Messenger(tcpSocket=tcpSocket)
    #receiver = mp.Process(target=serverReceiver, args=(sock,))
    sender = thr.Thread(target=udpTunnel, args=())
    #receiver.start()
    sender.start()

def connectToDevice(device,behindNat):
    global bridgeMessenger
    global serverMessenger
    if behindNat:
        bridgeMessenger=msg.Messenger()
        result=serverMessenger.askForConnectionToDevice(device,behindNat)
    else:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            myPublicIp=get('https://api.ipify.org').text
            sock.bind((myPublicIp,1102))
            result = serverMessenger.askForConnectionToDevice(device, behindNat,sock.getsockname())
        except Exception as e:
            print(e)
    return bridgeMessenger
        #result = serverMessenger.askForConnectionToDevice(device, behindNat)
        #serverMessenger = msg.Messenger(sock, add)


def getBridgesForUser(userID):
    result=serverMessenger.askForBridges(userID)
    bridges=result["response"]
    return bridges

def getDevicesForBridge(bridgeID):
    result=serverMessenger.askForBridgesDevices(bridgeID)
    devices=result["response"]
    return  devices


def authorizate(login,password):
    result=serverMessenger.sendAuthorizationRequest(login,password)
    if result["response"]=="access_granted":
        return int(result["UserID"])
    else:
        return False

def udpTunnel():
    global udpSocket
    print("sender started")
    while True:
        udpSocket.sendto(("keepalive connected as"+seenAs).encode(),('localhost', 1101))
        time.sleep(2)
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

