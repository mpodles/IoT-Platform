import logging
import socket
import sys
import multiprocessing as mp
import threading as thread
import time
import json
#import Server.Messenger as msg
from util import *
import Server.DatabaseConnection as dbc
#import Server.Messengers as messengers

global processesManager
global bridgesMessengers
global clientsMessengers
global tcpToUdpMap


# def clientReceiver(conn,add):
#     print("receiver started",add)
#     while True:
#         data=conn.recv(1024)
#         print(bytes.decode(data))
# def clientSender(conn,add):
#     print("sender started",add)
#     while True:
#         conn.sendall("elo".encode())
#         print("elo sent")
#         time.sleep(1)

# def bridgeReceiver(conn,add):
#     while True:
#         conn.recv(1024)
# def bridgeSender(conn,add):
#     while True:
#         conn.recv(1024)

# def handleClient(conn, add):
#     newClientMessenger= msg.Messenger(conn,add)
#     messengers.append(newClientMessenger)
#     print(messengers)
#
# def handleBridge(conn, add):
#     newClientMessenger = msg.Messenger(conn, add)
#     messengers.append(newClientMessenger)


def listenForBridges():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.1.26', 1100))
    sock.listen()
    #bridgesMessengers = {}
    while True:
        conn, add = sock.accept()
        newClientMessenger = Messenger(conn, add)
        bridgesMessengers[add]=newClientMessenger

def listenForClients():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost',1101))
    print(clientsMessengers)
    sock.listen()
    while True:
        conn, add = sock.accept()
        conn.sendall(str.encode(str(add)))
        newClientMessenger = Messenger(conn, add)
        try:
            clientsMessengers[add]=newClientMessenger
        except Exception as e:
            print (e)
        print(clientsMessengers)

def sendNotification():
    pass
def helpWithConnection():
    pass

def udpReceiver(socket):
    global tcpToUdpMap
    print("UDP receiver started")
    while True:
        data,addr = socket.recvfrom(1024)
        addrAndPort=bytes.decode(data)[22:].split(",")
        key= (str(addrAndPort[0][2:-1]),int(addrAndPort[1][:-1]))
        tcpToUdpMap[key]=tuple(addr)
        print(tcpToUdpMap)


class Messenger:
    socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    add=""
    messageId = 0
    receiverProcess=mp.Process
    #senderProcess=mp.Process
    def __init__(self,conn,add):
        self.socket=conn
        self.add=add
        self.receiverProcess = thread.Thread(target=self.receiver, args=())
        #self.senderProcess = mp.Process(target=self.sender, args=())
        self.receiverProcess.start()
        #self.senderProcess.start()


    def interpretMessage(self,data):
        print("received" ,data)
        parsedData=json.loads(data)
        msgID= int(parsedData["messageID"])
        self.messageId= msgID
        msgType = parsedData["type"]
        if msgType == "authRequest":
            self.handleAuthentication(parsedData)
        elif msgType == "bridgesRequest":
            self.handleBridgesRequest(parsedData)
        elif msgType == "devicesRequest":
            self.handleDevicesRequest(parsedData)
        elif msgType == "deviceConnectionRequest":
            self.handleDevicesConnectionRequest(parsedData)

    def handleBridgesRequest(self,data):
        userID=data["userID"]
        result = dbc.select("Bridges", rows="*", condition='WHERE UserID="' + userID +'"')
        dictionaryToJson={"type":"bridgesResponse","response":result}
        msg=self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleDevicesRequest(self,data):
        bridgeID=data["bridgeID"]
        result = dbc.select("Devices", rows="*", condition='WHERE BridgeID="' + bridgeID +'"')
        dictionaryToJson={"type":"devicesResponse","response":result}
        msg=self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleDevicesConnectionRequest(self,data):
        print(bridgesMessengers)
        print(clientsMessengers)
        deviceID,behindNat=data["deviceID"],data["behindNat"]
        result = dbc.select("Devices", rows="*", condition='WHERE DeviceID="' + deviceID +'"')
        if result.__len__() > 0:
            deviceAddress= result[0][1]
            deviceName= result[0][2]
            bridgeID =result[0][3]
            requestToBridgeDictToJson = {"type":"deviceConnectionRequest","deviceName":str(deviceName),"deviceAddress":str(deviceAddress)}
            req=bridgesMessengers[result[0][3]].constructMessage(requestToBridgeDictToJson)  # TODO
            bridgesMessengers[result[0][3]].send_msg(req)
            #dictionaryToJson = {"type": "devicesConnectionResponse", "response": }
        else:
            dictionaryToJson={"type":"devicesConnectionResponse","response":"deviceNotFound"}
        msg=self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleAuthentication(self,data):
        login,password=data["login"],data["password"]
        result=dbc.select("Users",rows="*",condition='WHERE login="'+login+'" AND password="'+password+'"')
        if  result.__len__()>0:
            userID=result[0][0]
            dictionaryToJson = {"type":"authResponse","response":"access_granted","UserID":userID}
        else:
            dictionaryToJson = {"type": "authResponse", "response": "access_denied","UserID":"0"}
        msg=self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg

    def receiver(self):
        global clientsMessengers
        global bridgesMessengers
        try:
            print("receiver started")
            while True:
                data=self.recv_msg()
                if data is not None:
                    self.interpretMessage(bytearray.decode(data))
        except Exception as e:
            print(e)
            if self in clientsMessengers.values():
                print("found self in clients")
                clientsMessengers={key: val for key, val in clientsMessengers.items() if val != self}
                print("deleted self")
            elif self in bridgesMessengers.values():
                print("found self in bridges")
                bridgesMessengers = {key: val for key, val in bridgesMessengers.items() if val != self}
                print("deleted self")
            else:
                print("didnt find myself")

    def recv_msg(self):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(msglen)

    def recvall(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        print("sent message ", msg)
        self.socket.sendall(msg)

    def sender(self):
        print("sender started")
        while True:
            self.socket.sendall("elo".encode())
            print(self.socket)
            time.sleep(5)


if __name__ == '__main__':

    global processesManager
    global bridgesMessengers
    global clientsMessengers
    global tcpToUdpMap

    bridgesMessengers = {}
    clientsMessengers = {}
    tcpToUdpMap ={}

    bridgesUdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsUdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bridgesUdpSocket.bind(("localhost", 1100))
    clientsUdpSocket.bind(("localhost", 1101))

    clientsUdpProcess = thread.Thread(target=udpReceiver, args=(clientsUdpSocket,))
    # clientsProcess.daemon = True
    clientsUdpProcess.start()
    bridgesUdpProcess = thread.Thread(target=udpReceiver, args=(bridgesUdpSocket,))
    # bridgesProcess.daemon = True
    bridgesUdpProcess.start()

    clientsProcess = thread.Thread(target=listenForClients, args=())
    #clientsProcess.daemon = True
    clientsProcess.start()
    bridgesProcess = thread.Thread(target=listenForBridges, args=())
    #bridgesProcess.daemon = True
    bridgesProcess.start()
