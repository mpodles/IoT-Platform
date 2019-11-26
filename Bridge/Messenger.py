import json
import socket
import time
import threading as thr
import multiprocessing as mp
import struct
import Bridge.Setup as setup
import Bridge.Options
import Bridge.Device

serverMessenger=None

clientMessenger=None

messengerForModules=None

udpSocket=None

seenAs=None #IMPORTANT FOR UDP TUNNEL

modulesSocket=None

messengersToModules=None

devicesInModule=None


def connectToServer(address='localhost',port=1100):
    global serverMessenger
    global seenAs
    #global tcpSocket
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.connect((address,port))
    seenAs=bytes.decode(tcpSocket.recv(1024))
    print("I'm seen as tcp: ",seenAs)
    serverMessenger = OutsideServerMessenger(tcpSocket=tcpSocket)
    #receiver = mp.Process(target=serverReceiver, args=(sock,))
    sender = thr.Thread(target=udpTunnel, args=())
    #receiver.start()
    sender.start()

def registerBridge():
    global serverMessenger
    serverMessenger.sendRegistrationRequest()

def udpTunnel():
    global udpSocket
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("udp sender started")
    while True:
        udpSocket.sendto(("keepalive connected as"+seenAs).encode(),('localhost', 1100))
        time.sleep(2)

def awaitForModules():
    global modulesSocket
    global messengersToModules
    global devicesInModule
    devicesInModule = {}
    messengersToModules={}
    modulesSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    modulesSocket.bind(('localhost',2200))
    modulesSocket.listen()
    while True:
        conn,add= modulesSocket.accept()
        newModulesMessenger=BridgeToModuleMessenger(conn,add)
        messengersToModules[add]= newModulesMessenger

def connectToBridge():
    global messengerForModules
    socketForModules= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketForModules.connect(('localhost',2200))
    messengerForModules=ModuleToBridgeMessenger(tcpSocket=socketForModules)

def registerDevices(devices):
    global messengerForModules
    messengerForModules.sendDevicesToBridge(devices)

def registerOptions(options):
    global messengerForModules
    messengerForModules.sendOptionsToBridge(options)

def sendDataFromDevice(device,data):
    global messengerForModules
    messengerForModules.sendDataFromDevice(device,data)

def getData():
    global messengerForModules
    data= messengerForModules.receive()
    return data





class BridgeToModuleMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiverThread=thr.Thread
    messageId = 0
    add=""
    def __init__(self,tcpSocket,add):
        self.add=add
        self.tcpSocket=tcpSocket
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        self.receiverThread.start()


    def interpretMessage(self,data):
        print("received" ,data)
        parsedData=json.loads(data)
        msgID= int(parsedData["messageID"])
        self.messageId= msgID
        msgType = parsedData["type"]
        if msgType == "devicesToBridge":
            self.handleDevicesFromModules(parsedData)
        elif msgType == "optionsToBridge":
            self.handleOptionsFromModules(parsedData)
        elif msgType == "dataFromDevice":
            self.handleDataFromDevices(parsedData)


    def handleDataFromDevices(self,data):
        global clientMessenger
        payload= data["data"]
        deviceName=data["deviceName"]
        deviceAddress=data["deviceAddress"]
        clientMessenger.sendDataFromDevice(deviceName,deviceAddress,payload)


    def handleDevicesFromModules(self,data):
        global serverMessenger
        global devicesInModule
        devices=data["devices"]
        for device in devices:
            deviceAddress=device["address"]
            deviceName=device["name"]
            devicesInModule[(deviceName,deviceAddress)]=self.add
        print(devicesInModule)
        serverMessenger.sendDevicesRegistrationRequest(devices)


    def sendDataToDevice(self,device,data):
        print(device)
        device=tuple(device)
        print(device)
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"dataFromDevice"' \
                              ',"deviceName":"' + device[0] + '","deviceAddress":"' + device[1] + '","payload":"' + data + '"}'
        self.send_msg(msg)

    def handleOptionsFromModules(self,data):
        global serverMessenger
        options =data["options"]
        serverMessenger.sendOptionRegistrationRequest(options)


    def getResult(self):
        try:
            print("gettingResult")
            data=bytearray.decode(self.recv_msg())
            print("result is",data)
            dictData=json.loads(data)
            return dictData
                # self.interpretMessage(data)
        except Exception as e:
            print(e)


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


    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        self.messageId=self.messageId+1
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.tcpSocket.sendall(msg)
        print("sent message ",msg)


    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg


    def receiver(self):
        global messengersToModules
        global clientMessenger
        try:
            print("receiver started")
            while True:
                try:
                    data=self.recv_msg()
                    if data is not None:
                        self.interpretMessage(bytearray.decode(data))
                except Exception as e:
                    print(e)
                    if clientMessenger is not None and clientMessenger.current is self:
                        print("Module was being used for client")
                        clientMessenger.moduleDisconnected=True
                    if self in messengersToModules.values():
                        print("found self in messengers to modules")
                        messengersToModules = {key: val for key, val in messengersToModules.items() if val != self}
                        print("deleted self")
                    else:
                        print("didnt find myself")

        except Exception as e:
            print(e)






class ModuleToBridgeMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #receiverThread=thr.Thread
    messageId = 0
    def __init__(self,tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.tcpSocket=tcpSocket
        #self.receiverThread = thr.Thread(target=self.receiver, args=())
        #self.receiverThread.start()


    def sendDataFromDevice(self,device,data):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"dataFromDevice", ' \
            '"deviceName":"' + device.name + '", "deviceAddress":"'+device.address+'" ,"data":"' + str(data) + '"}'
        self.send_msg(msg)

    def sendOptionsToBridge(self,options):
        optionsList = []
        for option in options:
            dictionaryToJson = {"type": option.type, "options": option.options}
            optionsList.append(dictionaryToJson)
        optionsStr = json.dumps(optionsList)
        msg = '{"messageID":"' + str(self.messageId) + '",' \
                                                       '"type":"optionsToBridge","options":' + optionsStr + '}'
        self.send_msg(msg)

    def sendDevicesToBridge(self,devices):
        devicesList=[]
        for device in devices:
            dictionaryToJson={}
            dictionaryToJson = {"type": device.type, "name": device.name, "address": device.address}
            devicesList.append(dictionaryToJson)
        devicesStr=json.dumps(devicesList)
        msg='{"messageID":"'+str(self.messageId)+'",' \
        '"type":"devicesToBridge","devices":'+devicesStr+'}'
        self.send_msg(msg)


    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg

    def getResult(self):
        try:
            print("gettingResult")
            data=bytearray.decode(self.recv_msg())
            print("result is",data)
            dictData=json.loads(data)
            return dictData
                # self.interpretMessage(data)
        except Exception as e:
            print(e)


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


    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        self.messageId=self.messageId+1
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.tcpSocket.sendall(msg)
        print("sent message ",msg)


    def receive(self):
        try:
            while True:
                data=self.recv_msg()
                if data is not None:
                    return data
        except Exception as e:
            print(e)


    # def interpretMessage(self,data):
    #     print("received" ,data)
    #     parsedData=json.loads(data)
    #     msgID= int(parsedData["messageID"])
    #     self.messageId= msgID
    #     msgType = parsedData["type"]
    #     if msgType == "devicesToBridge":
    #         self.handleDevicesFromModules(parsedData)
    #
    #
    #


class OutsideServerMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    seenAs=""
    #result={}
    receiverThread=thr.Thread
    senderThread=thr.Thread
    messageId = 0
    def __init__(self,tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM),udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)):
        self.tcpSocket=tcpSocket
        #self.tcpSocket.setblocking(0)
        self.udpSocket=udpSocket
        #self.seenAs=seenAs
        #self.senderThread= thr.Thread(target=self.sender)
        #self.senderThread.start()
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        #self.senderProcess = mp.Process(target=self.sender, args=())
        self.receiverThread.start()
        #self.senderProcess.start()


    def sendDataFromDevice(self,deviceName,deviceAddress,data):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"dataFromDevice",' \
        '"deviceName":"' + deviceName + '","deviceAddress":"' + deviceAddress + '", "data":"'+data+'"}'
        self.send_msg(msg)

    def sendRegistrationRequest(self):
        msg='{"messageID":"'+str(self.messageId)+'","type":"registrationRequest","bridgeName":"'+setup.bridgeName+'","bridgeUser":"'+setup.userName+'"}'
        self.send_msg(msg)


    def sendDevicesRegistrationRequest(self,devices):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"devicesRegistrationRequest","bridgeName":"' + setup.bridgeName + '","devices":"' + str(devices) + '"}'
        self.send_msg(msg)

    def sendOptionRegistrationRequest(self,options):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"optionsRegistrationRequest","options":"' + str(options) + '"}'
        self.send_msg(msg)

    def handleDevicesConnectionRequest(self,data):
        global clientMessenger
        global udpSocket
        global messengersToModules
        if clientMessenger is not None:
            print("current clientMsg ",clientMessenger)
        else:
            print("current clientMsg is None")
        deviceName=data["deviceName"]
        deviceAddress=data["deviceAddress"]
        clientAddress=data["clientAddress"]
        clientBehindNat=bool(data["behindNat"])
        print(devicesInModule)
        moduleAddress=devicesInModule[(deviceName,deviceAddress)]
        currentModule=messengersToModules[moduleAddress]
        print(clientAddress)
        if clientBehindNat:
            clientMessenger= OutsideClientMessenger(udpSocket=udpSocket,module=currentModule,address=clientAddress,device=(deviceName,deviceAddress))
        else:
            newUdpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            clientMessenger = OutsideClientMessenger(udpSocket=newUdpSocket,module=currentModule,address=clientAddress,device=(deviceName,deviceAddress))

    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg

    def getResult(self):
        try:
            print("gettingResult")
            data=bytearray.decode(self.recv_msg())
            print("result is",data)
            dictData=json.loads(data)
            return dictData
                # self.interpretMessage(data)
        except Exception as e:
            print(e)


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


    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        self.messageId=self.messageId+1
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.tcpSocket.sendall(msg)
        print("sent message ",msg)


    def receiver(self):
        try:
            print("receiver started")
            while True:
                data=self.recv_msg()
                if data is not None:
                    self.interpretMessage(bytearray.decode(data))
        except Exception as e:
            print(e)

    def interpretMessage(self,data):
        print("received" ,data)
        parsedData=json.loads(data)
        msgID= int(parsedData["messageID"])
        self.messageId= msgID
        msgType = parsedData["type"]
        if msgType == "deviceConnectionRequest":
            self.handleDevicesConnectionRequest(parsedData)
        #     self.handleAuthentication(parsedData)
        # elif msgType == "bridgesRequest":
        #     self.handleBridgesRequest(parsedData)
        # elif msgType == "devicesRequest":
        #     self.handleDevicesRequest(parsedData)
        # elif msgType == "devicesConnectionRequest":
        #     self.handleDevicesConnectionRequest(parsedData)




class OutsideClientMessenger:
    udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    receiverThread=thr.Thread
    clientAddress=""
    device=""
    stopSender= False
    messageId = 0
    currentModule=None
    moduleDisconnected=False
    def __init__(self,udpSocket,module,address,device):
        self.currentModule=module
        self.udpSocket=udpSocket
        self.clientAddress=(address[0],address[1])
        self.device=device
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        self.receiverThread.start()
        self.senderThread = thr.Thread(target=self.keepaliveSender())
        self.senderThread.start()
        self.moduleCheckerThread=thr.Thread(target=self.moduleChecker)
        self.moduleCheckerThread.start()


    def sendDataFromDevice(self,deviceName,deviceAddress,data):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"dataFromDevice"' \
        ',"deviceName":"' + deviceName + '","deviceAddress":"' +deviceAddress + '","payload":"'+data+'"}'
        self.send_msg(msg)

    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg


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
            packet = self.udpSocket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data


    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        self.messageId=self.messageId+1
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.udpSocket.sendto(msg,self.clientAddress)
        print("sent message ",msg)

    def send_udp_msg(self,msg):
        self.udpSocket.sendto((msg.encode(), (str(self.clientAddress[0]), int(self.clientAddress[1]))))
        print("sent message ",msg)

    def receiver(self):
        global clientMessenger
        try:
            print("receiver started")
            while True:
                data, addr = self.udpSocket.recvfrom(4096)
                if data is not None:
                    self.interpretMessage(bytes.decode(data))
        except Exception as e:
            self.stopSender= True

    def keepaliveSender(self):
        while True:
            if self.stopSender:
                print("exiting sender")
                return
            self.udpSocket.sendto(("k!e@e#p$a%l^i&v*e(").encode(), (str(self.clientAddress[0]),int(self.clientAddress[1])))
            self.udpSocket.sendto(("eldo").encode(),
                                  (str(self.clientAddress[0]), int(self.clientAddress[1])))
            time.sleep(2)

    def moduleChecker(self):
        while True:
            if self.moduleDisconnected:
                self.stopSender=True
                self.send_udp_msg("ERROR: Module disconnected")
                print("module disconnected")



    def interpretMessage(self,data):
        if data == "k!e@e#p$a%l^i&v*e(":
            print("keepalive received")
        elif data=="c!l@i#e$n%t^s&t*o(p)":
            self.stopSender=True
        else:
            print("receive ",data," from client")
            self.currentModule.sendDataToDevice(self.device,data)
        # if msgType == "devicesToBridge":
        #     self.handleDevicesFromModules(parsedData)
