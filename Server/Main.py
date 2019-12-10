import logging
import socket
import sys
import multiprocessing as mp
import threading as thread
import time
import json
import re
import struct
# import Server.Messenger as msg
import DatabaseConnection as dbc

# import Server.Messengers as messengers

processesManager = None

bridgesMessengers = None

clientsMessengers = None

tcpToUdpMap = None


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


def listenForBridges(sock):
    sock.listen()
    while True:
        conn, add = sock.accept()
        conn.sendall(str.encode(str(add)))
        newBridgeMessenger = Messenger(conn, add)
        try:
            bridgesMessengers[add] = newBridgeMessenger
        except Exception as e:
            print("exception adding client messenger to list", e)
        print(bridgesMessengers)


def listenForClients(sock):
    sock.listen()
    while True:
        conn, add = sock.accept()
        conn.sendall(str.encode(str(add)))
        newClientMessenger = Messenger(conn, add)
        try:
            clientsMessengers[add] = newClientMessenger
        except Exception as e:
            print("exception adding client messenger to list", e)
        print(clientsMessengers)


def sendNotification():
    pass


def helpWithConnection():
    pass


def udpReceiver(socket):
    global tcpToUdpMap
    print("UDP receiver started")
    while True:
        data, addr = socket.recvfrom(1024)
        addrAndPort = bytes.decode(data)[22:].split(",")
        key = (str(addrAndPort[0][2:-1]), int(addrAndPort[1][:-1]))
        tcpToUdpMap[key] = tuple(addr)
        # print(tcpToUdpMap)


class Messenger:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerAdd = ""
    messageId = 0
    receiverProcess = mp.Process

    # senderProcess=mp.Process
    def __init__(self, conn, peerAdd):
        self.tcpSocket = conn
        add = str(peerAdd).replace(",", ":")
        self.peerAdd = re.sub('[^A-Za-z0-9.:]+', '', add)
        self.receiverThread = thread.Thread(target=self.receiver, args=())
        # self.senderThread = thread.Thread(target=self.sender, args=())
        self.receiverThread.start()
        # self.senderThread.start()

    def interpretMessage(self, data):
        print("received", data)
        if data == "keepalive":
            return
        parsedData = json.loads(data)
        msgID = int(parsedData["messageID"])
        self.messageId = msgID
        msgType = parsedData["type"]
        if msgType == "authorizationRequest":
            self.handleAuthentication(parsedData)
        elif msgType == "bridgesRequest":
            self.handleBridgesRequest(parsedData)
        elif msgType == "devicesRequest":
            self.handleDevicesRequest(parsedData)
        elif msgType == "deviceConnectionRequest":
            self.handleDevicesConnectionRequest(parsedData)
        elif msgType == "registrationRequest":
            self.handleBridgesRegistration(parsedData)
        elif msgType == "devicesRegistrationRequest":
            self.handleDevicesRegistration(parsedData)
        elif msgType == "optionsRegistrationRequest":
            self.handleOptionsRegistration(parsedData)
        elif msgType == "devicesDeletionRequest":
            self.handleDevicesDeletion(parsedData)

    def handleDevicesDeletion(self, data):
        bridgeName = data["bridgeName"]
        devices = data["devices"]

        devices = devices.replace("'", '"')
        devices = devices.replace("(", '[')
        devices = devices.replace(")", ']')
        devices = json.loads(devices)
        check = dbc.select("bridges", rows="*",
                           condition='Name="' + str(bridgeName) + '"')
        if check.__len__() > 0:
            bridgeId = check[0][0]
            for device in devices:
                deviceName = device[0]
                deviceAddress = device[1]
                check2 = dbc.select("devices", rows="*",
                                    condition='Address="' + str(deviceAddress) + '" AND '
                                                                                 'BridgeID="' + str(bridgeId) + '" ')
                if check2.__len__() > 0:
                    print("device exists and trying to delete")
                    condition = 'Name= "' + deviceName + '" AND BridgeID="' + str(bridgeId) + '" AND Address="' + str(
                        deviceAddress) + '"'
                    dbc.delete("devices", condition)
                else:
                    print("device to delete not found")
        else:
            print("No such bridge found")

    def handleDevicesRegistration(self, data):
        bridgeName = data["bridgeName"]
        devices = data["devices"]
        devices = devices.replace("'", '"')
        devices = json.loads(devices)
        check = dbc.select("bridges", rows="*",
                           condition='Name="' + str(bridgeName) + '"')
        if check.__len__() > 0:
            bridgeId = check[0][0]
            for device in devices:
                deviceName = device["name"]
                deviceAddress = device["address"]
                deviceType = device["type"]
                check2 = dbc.select("devices", rows="*",
                                    condition='Address="' + str(deviceAddress) + '" AND '
                                                                                 'BridgeID="' + str(bridgeId) + '" ')
                if check2.__len__() > 0:
                    print("device exists")
                    query = 'Name= "' + deviceName + '" WHERE BridgeID="' + str(bridgeId) + '" AND Address="' + str(
                        deviceAddress) + '"'
                    dbc.update("devices", query)
                else:
                    query = '( ' + str(bridgeId) + ',"' + str(deviceAddress) + '","' + str(deviceType) + '","' + str(
                        deviceName) + '")'
                    dbc.insert("devices", "(BridgeID,Address,Type,Name)", query)
        else:
            print("No such bridge found")

    def handleOptionsRegistration(self, data):
        options = data["options"]
        options = options.replace("'", '"')
        options = json.loads(options)
        for option in options:
            type = option["type"]
            optionsList = option["options"]
            for optionInstance in optionsList:
                check = dbc.select("options", rows="*",
                                   condition='Type="' + str(type) + '" AND DeviceOption="' + str(optionInstance) + '"')
                if check.__len__() > 0:
                    print("Option exists ")
                else:
                    query = '( "' + str(type) + '","' + optionInstance + '")'
                    dbc.insert("options", "(Type,DeviceOption)", query)

    def handleBridgesRegistration(self, data):
        bridgeName, bridgeUser = data["bridgeName"], data["bridgeUser"]
        userCheck = dbc.select("users", rows="*", condition='Login="' + bridgeUser + '"')
        if userCheck.__len__() > 0:
            userId = userCheck[0][0]
            check = dbc.select("bridges", rows="*",
                               condition='Name="' + str(bridgeName) + '" AND UserID="' + str(userId) + '"')
            if check.__len__() > 0:
                bridgeId = check[0][0]
                print("Updating bridge ", bridgeId)
                query = 'Address= "' + str(self.peerAdd) + '" WHERE BridgeID=' + str(bridgeId)
                dbc.update("bridges", query)
                dictionaryToJson = {"type": "registrationResponse", "response": "bridgeUpdated"}
            else:
                print("Inserting new bridge")
                query = '( ' + str(userId) + ',"' + self.peerAdd + '","' + str(bridgeName) + '")'
                dbc.insert("bridges", "(UserID,Address,Name)", query)
                dictionaryToJson = {"type": "registrationResponse", "response": "bridgeRegistered"}
            msg = self.constructMessage(dictionaryToJson)
            self.send_msg(msg)
        else:
            dictionaryToJson = {"type": "registrationResponse", "response": "userNotFound"}
            msg = self.constructMessage(dictionaryToJson)
            self.send_msg(msg)

    def handleBridgesRequest(self, data):
        userID = data["userID"]
        result = dbc.select("bridges", rows="*", condition='UserID="' + userID + '"')
        dictionaryToJson = {"type": "bridgesResponse", "response": result}
        msg = self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleDevicesRequest(self, data):
        bridgeID = data["bridgeID"]
        result = dbc.select("devices", rows="*", condition='BridgeID="' + bridgeID + '"')
        dictionaryToJson = {"type": "devicesResponse", "response": result}
        msg = self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleDevicesConnectionRequest(self, data):
        print(bridgesMessengers)
        print(clientsMessengers)
        deviceID, behindNat = data["deviceID"], bool(data["behindNat"])
        result = dbc.select("devices", rows="*", condition='DeviceID="' + deviceID + '"')
        if result.__len__() > 0:
            deviceAddress = result[0][1]
            deviceName = result[0][2]
            deviceType = result[0][3]
            clientAddressKey = (str(self.peerAdd.split(":")[0]), int(self.peerAdd.split(":")[1]))
            options = self.getOptionsByType(deviceType)
            bridgeID = result[0][4]
            findBridge = dbc.select("bridges", rows="Address", condition='BridgeID="' + str(bridgeID) + '"')
            bridgeAddress = findBridge[0][0]
            bridgeAddressKey = (str(bridgeAddress.split(":")[0]), int(bridgeAddress.split(":")[1]))
            requestToBridgeDictToJson = {"type": "deviceConnectionRequest", "deviceName": str(deviceName),
                                         "deviceAddress": str(deviceAddress)}
            dictionaryToJson = {"type": "devicesConnectionResponse", "response": "sentAddressToBridge",
                                "options": options}
            if behindNat:
                print(tcpToUdpMap)
                try:
                    requestToBridgeDictToJson["clientAddress"] = tcpToUdpMap[clientAddressKey]
                    bridgesUDP = tcpToUdpMap[bridgeAddressKey]
                except Exception as e:
                    print("tcpToUdp exception:", e)
                    dictionaryToJson = {"type": "devicesConnectionResponse", "response": "UDPmappingNotFound"}
                    msg = self.constructMessage(dictionaryToJson)
                    self.send_msg(msg)
                    return
                dictionaryToJson["bridgeAddress"] = bridgesUDP
                requestToBridgeDictToJson["behindNat"] = True
            else:
                requestToBridgeDictToJson["clientAddress"] = data["clientAddress"]
                requestToBridgeDictToJson["behindNat"] = False

            currentBridgeMessenger = bridgesMessengers[bridgeAddressKey]
            req = currentBridgeMessenger.constructMessage(requestToBridgeDictToJson)
            currentBridgeMessenger.send_msg(req)
            # dictionaryToJson = {"type": "devicesConnectionResponse", "response": }
        else:
            dictionaryToJson = {"type": "devicesConnectionResponse", "response": "deviceNotFound"}
        msg = self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleAuthentication(self, data):
        login, password = data["login"], data["password"]
        result = dbc.select("users", rows="*", condition='Login="' + login + '" AND Password="' + password + '"')
        if result.__len__() > 0:
            userID = result[0][0]
            dictionaryToJson = {"type": "authorizationResponse", "response": "access_granted", "UserID": userID}
        else:
            dictionaryToJson = {"type": "authorizationResponse", "response": "access_denied", "UserID": "0"}
        msg = self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def getOptionsByType(self, type):
        result = dbc.select("options", rows="*", condition='Type="' + type + '"')
        options = []
        for option in result:
            options.append(option[1])
        return options

    def constructMessage(self, data):
        data["messageID"] = self.messageId
        msg = json.dumps(data)
        return msg

    def receiver(self):
        global clientsMessengers
        global bridgesMessengers
        try:
            print("receiver started")
            while True:
                data = self.recv_msg()
                if data is not None:
                    self.interpretMessage(bytearray.decode(data))
                if data is None:
                    raise Exception("GOT NONE AS DATA")
        except Exception as e:
            print("receiver exception", e)
            if self in clientsMessengers.values():
                print("found self in clients")
                clientsMessengers = {key: val for key, val in clientsMessengers.items() if val != self}
                print("deleted self")
            elif self in bridgesMessengers.values():
                print("found self in bridges")
                self.deleteBridgeAndDevicesOnLostConnection()
                bridgesMessengers = {key: val for key, val in bridgesMessengers.items() if val != self}
                print("deleted self")
            else:
                print("didnt find myself")

    def deleteBridgeAndDevicesOnLostConnection(self):
        check = dbc.select("bridges", rows="BridgeID",
                           condition='Address="' + str(self.peerAdd) + '" ')
        if check.__len__() > 0:
            bridgeID = check[0][0]
            dbc.delete("devices", 'BridgeID="' + str(bridgeID) + '"')
            print("bridge's devices deleted")
            dbc.delete("bridges", 'BridgeID="' + str(bridgeID) + '"')
            print("bridge deleted")

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
            packet = self.tcpSocket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def send_msg(self, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.tcpSocket.sendall(msg)
        print("sent message ", msg, " on address ", self.peerAdd)

    def sender(self):
        print("sender started")
        while True:
            self.tcpSocket.sendall("elo".encode())
            print(self.tcpSocket)
            time.sleep(5)


if __name__ == '__main__':
    #dbc.createDatabaseAndTables("192.168.1.12","root","password")
    myIpAdd = "localhost"

    dbc.connectToDatabase("192.168.1.12", "root", "password")
    dbc.clearTables()

    bridgesMessengers = {}
    clientsMessengers = {}
    tcpToUdpMap = {}

    bridgesUdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsUdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bridgesUdpSocket.bind((myIpAdd, 1100))
    clientsUdpSocket.bind((myIpAdd, 1101))

    clientsUdpProcess = thread.Thread(target=udpReceiver, args=(clientsUdpSocket,))
    # clientsProcess.daemon = True
    clientsUdpProcess.start()
    bridgesUdpProcess = thread.Thread(target=udpReceiver, args=(bridgesUdpSocket,))
    # bridgesProcess.daemon = True
    bridgesUdpProcess.start()

    bridgesTcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsTcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    bridgesTcpSocket.bind((myIpAdd, 1100))
    clientsTcpSocket.bind((myIpAdd, 1101))

    clientsProcess = thread.Thread(target=listenForClients, args=(clientsTcpSocket,))
    # clientsProcess.daemon = True
    clientsProcess.start()
    bridgesProcess = thread.Thread(target=listenForBridges, args=(bridgesTcpSocket,))
    # bridgesProcess.daemon = True
    bridgesProcess.start()
