import logging
import socket
import sys
import time
from util import *
import multiprocessing as mp
import threading as thr
from requests import get

import Client.Messenger as msg

serverMessenger=None

bridgeMessenger=None

tcpSocket=None

udpSocket=None

seenAs=None

connectedToServer=False

stopUdpSender=False

def connectToServer(address='zace.hopto.org',port=1101):
    global serverMessenger
    global seenAs
    global tcpSocket
    global udpSocket
    global connectedToServer
    if not connectedToServer:
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.connect((address,port))
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        seenAs=bytes.decode(tcpSocket.recv(1024))
        print("I'm seen as tcp: ",seenAs)
        serverMessenger = msg.ServerMessenger(tcpSocket=tcpSocket)
        sender = thr.Thread(target=udpTunnel, args=(address,))
        sender.start()
        isConnectedToServer=True
    else:
        raise Exception("already connected")


def connectToDevice(device,behindNat):
    global bridgeMessenger
    global serverMessenger
    global udpSocket
    options=None
    if behindNat:
        result=serverMessenger.askForConnectionToDevice(device,behindNat)
        response=result["response"]
        if response !="sentAddressToBridge":
            raise Exception(response)
        bridgeAdd=result["bridgeAddress"]
        options = result["options"]
        bridgeMessenger = msg.BridgeMessenger(udpSocket=udpSocket,bridgeAddress=(bridgeAdd[0],bridgeAdd[1]))
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind((tuple(seenAs)[0],1102))
        except Exception as e:
            print(e)
            sock.bind((tcpSocket.getsockname()[0],1102))
        result = serverMessenger.askForConnectionToDevice(device, behindNat,sock.getsockname())
        options=result["options"]
        bridgeMessenger=msg.BridgeMessenger(udpSocket=sock)

    return bridgeMessenger,options
        #result = serverMessenger.askForConnectionToDevice(device, behindNat)
        #serverMessenger = msg.Messenger(sock, add)

def disconnectFromServer():
    global serverMessenger
    global connectedToServer
    global stopUdpSender
    connectedToServer = False
    stopUdpSender=True
    serverMessenger=None

def receiveDataFromBridge():
    global bridgeMessenger
    return bridgeMessenger.receive()

def sendDataToBridge(dictionaryToJson):
    global bridgeMessenger
    msg = bridgeMessenger.constructMessage(dictionaryToJson)
    bridgeMessenger.send_udp_msg(msg)


def disconnectFromBridge():
    global bridgeMessenger
    if bridgeMessenger is not None:
        bridgeMessenger.send_udp_msg("c!l@i#e$n%t^s&t*o(p)")
        bridgeMessenger.stopSender=True
    bridgeMessenger=None

def getBridgesForUser(userID):
    result=serverMessenger.askForBridges(userID)
    bridges=result["response"]
    return bridges

def getDevicesForBridge(bridgeID):
    result=serverMessenger.askForBridgesDevices(bridgeID)
    devices=result["response"]
    return  devices


def authorize(login,password):
    result=serverMessenger.sendAuthorizationRequest(login,password)
    if result["response"]=="access_granted":
        return int(result["UserID"])
    else:
        raise Exception("access not granted")

def udpTunnel(address):
    global udpSocket
    print("sender started")
    while True:
        if stopUdpSender:
            return
        udpSocket.sendto(("keepalive connected as"+seenAs).encode(),(address, 1101))
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

