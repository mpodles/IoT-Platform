import json
import socket
import time
import threading as thr
import struct
import Bridge.Setup as setup
from datetime import datetime
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

boundDevices=None


def connectToServer(address='localhost',port=1100):
    global serverMessenger
    global seenAs
    #global tcpSocket
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.connect((address,port))
    seenAs=bytes.decode(tcpSocket.recv(1024))
    print("I'm seen as tcp: ",seenAs)
    serverMessenger = OutsideServerMessenger(tcpSocket=tcpSocket)

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
    global boundDevices
    boundDevices={}
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
    currentTime=datetime.now().time()
    messengerForModules.sendDataFromDevice(device,data,currentTime)


def getData():
    global messengerForModules
    data= messengerForModules.receive()
    return data


def bind(device,on_data,on_option):
    global boundDevices
    boundDevices[(device.name,device.address)]=(on_data,on_option)




class BridgeToModuleMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiverThread=thr.Thread
    messageId = 0
    add=""
    stopReceiver=False
    def __init__(self,tcpSocket,add):
        self.add=add
        self.tcpSocket=tcpSocket
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        self.receiverThread.start()


    def interpretMessage(self,data):
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
        if clientMessenger is not None:
            payload= data["data"]
            deviceName=data["deviceName"]
            deviceAddress=data["deviceAddress"]
            time=data["time"]
            if clientMessenger.device==(deviceName,deviceAddress):
                clientMessenger.sendDataFromDevice(deviceName,deviceAddress,payload,time)


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
        device=tuple(device)
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"dataFromDevice"' \
                              ',"deviceName":"' + device[0] + '","deviceAddress":"' + device[1] + '","payload":"' + data + '"}'
        self.send_msg(msg)

    def handleOptionsFromModules(self,data):
        global serverMessenger
        options =data["options"]
        serverMessenger.sendOptionRegistrationRequest(options)


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
        print("sent message to module",msg)


    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg


    def receiver(self):
        global messengersToModules
        global clientMessenger
        try:
            while True:
                if self.stopReceiver:
                    return
                try:
                    data=self.recv_msg()
                    if data is not None:
                        self.interpretMessage(bytearray.decode(data))
                except Exception as e:
                    print("error at bridge to module receiver+interpreter", e)
                    global devicesInModule
                    global serverMessenger
                    devicesToDelete = [key for key, val in devicesInModule.items() if val == (self.add)]
                    devicesInModule={key: val for key, val in devicesInModule.items() if val != (self.add)}
                    serverMessenger.sendDevicesDeletionRequest(devicesToDelete)
                    self.stopReceiver=True
                    #print("clientmessenger is ",clientMessenger)
                    if clientMessenger is not None and clientMessenger.currentModule is self:
                        #print("Module was being used for client")
                        clientMessenger.moduleDisconnected=True
                    if self in messengersToModules.values():
                        #print("found self in messengers to modules")
                        messengersToModules = {key: val for key, val in messengersToModules.items() if val != self}
                        print("deleted self")
                    else:
                        print("didnt find myself")

        except Exception as e:
            print("error at bridge to module receiver+interpreter at outer level STRANGE BEHAVIOUR", e)






class ModuleToBridgeMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiverThread=thr.Thread
    messageId = 0
    def __init__(self,tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.tcpSocket=tcpSocket
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        self.receiverThread.start()


    def sendDataFromDevice(self,device,data,time):
        msg = '{"messageID":"' + str(self.messageId) + '","type":"dataFromDevice", ' \
            '"deviceName":"' + device.name + '", "deviceAddress":"'+device.address+'" ,"data":"' + str(data) + '","time":"' + str(time) +'"}'
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
        print("sent message to bridge ",msg)


    def receive(self):
        try:
            while True:
                data=self.recv_msg()
                if data is not None:
                    return data
        except Exception as e:
            print(e)


    def receiver(self):
        print("receiver started")
        while True:
            try:
                data=self.recv_msg()
                if data is not None:
                    self.interpretMessage(bytearray.decode(data))
            except Exception as e:
                return


    def interpretMessage(self,data):
        global boundDevices
        print("module received" ,data)
        data=data.replace('"{','{')
        data=data.replace('}"','}')
        parsedData=json.loads(data)
        print(parsedData)
        msgID= int(parsedData["messageID"])
        self.messageId= msgID
        clientMessage = parsedData["payload"]
        msgType=clientMessage["type"]
        deviceName=clientMessage["deviceName"]
        deviceAddress = clientMessage["deviceAddress"]
        data= clientMessage["payload"]
        print(boundDevices)
        print(deviceName,deviceAddress,data)
        if msgType == "consoleMessage":
            try:
                functions = boundDevices[(deviceName, deviceAddress)]
                functions[0](data)
            except Exception as e:
                print("Error, device not bound: ",e)
        elif msgType =="consoleCommand":
            command=clientMessage["command"]
            try:
                functions=boundDevices[(deviceName,deviceAddress)]
                functions[1](command,data)
            except Exception as e:
                print("Error, device not bound: ",e)






class OutsideServerMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    seenAs=""
    receiverThread=thr.Thread
    senderThread=thr.Thread
    messageId = 0
    def __init__(self,tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM),udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)):
        self.tcpSocket=tcpSocket
        #self.tcpSocket.setblocking(0)
        self.udpSocket=udpSocket
        #self.seenAs=seenAs
        self.senderThread= thr.Thread(target=self.sender)
        self.senderThread.start()
        self.receiverThread = thr.Thread(target=self.receiver, args=())

        self.receiverThread.start()
        #self.senderProcess.start()


    # def sendDataFromDevice(self,deviceName,deviceAddress,data):
    #     msg = '{"messageID":"' + str(
    #         self.messageId) + '","type":"dataFromDevice",' \
    #     '"deviceName":"' + deviceName + '","deviceAddress":"' + deviceAddress + '", "data":"'+data+'"}'
    #     self.send_msg(msg)


    def sendRegistrationRequest(self):
        msg='{"messageID":"'+str(self.messageId)+'","type":"registrationRequest","bridgeName":"'+setup.bridgeName+'","bridgeUser":"'+setup.userName+'"}'
        self.send_msg(msg)


    def sendDevicesRegistrationRequest(self,devices):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"devicesRegistrationRequest","bridgeName":"' + setup.bridgeName + '","devices":"' + str(devices) + '"}'
        self.send_msg(msg)


    def sendDevicesDeletionRequest(self,devices):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"devicesDeletionRequest","bridgeName":"' + setup.bridgeName + '","devices":"' + str(
            devices) + '"}'
        self.send_msg(msg)


    def sendOptionRegistrationRequest(self,options):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"optionsRegistrationRequest","options":"' + str(options) + '"}'
        self.send_msg(msg)


    def handleDevicesConnectionRequest(self,data):
        global udpSocket
        global messengersToModules
        global clientMessenger
        deviceName=data["deviceName"]
        deviceAddress=data["deviceAddress"]
        clientAddress=data["clientAddress"]
        clientBehindNat=bool(data["behindNat"])
        #print(devicesInModule)
        moduleAddress=devicesInModule[(deviceName,deviceAddress)]
        currentModule=messengersToModules[moduleAddress]
        #print(clientAddress)
        if clientBehindNat:
            clientMessenger= OutsideClientMessenger(udpSocket=udpSocket,module=currentModule,address=clientAddress,device=(deviceName,deviceAddress))
        else:
            newUdpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            clientMessenger = OutsideClientMessenger(udpSocket=newUdpSocket,module=currentModule,address=clientAddress,device=(deviceName,deviceAddress))


    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg


    def sender(self):
        while True:
            time.sleep(2)
            self.send_msg("keepalive")


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
        #print("sent message to server  ",msg)


    def receiver(self):
        try:
            print("receiver started")
            while True:
                data=self.recv_msg()
                if data is not None:
                    self.interpretMessage(bytearray.decode(data))
        except Exception as e:
            print("error in server receiver ", e)


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
    stopChecker = False
    stopReceiver =False
    def __init__(self,udpSocket,module,address,device):
        self.stopSender = False
        self.moduleDisconnected = False
        self.stopChecker = False
        self.stopReceiver = False
        self.currentModule=module
        self.udpSocket=udpSocket
        self.clientAddress=(address[0],address[1])
        self.device=device
        self.receiverThread = thr.Thread(target=self.receiver, args=())
        self.receiverThread.start()

        self.senderThread = thr.Thread(target=self.keepaliveSender)
        self.senderThread.start()

        self.moduleCheckerThread=thr.Thread(target=self.moduleChecker)
        self.moduleCheckerThread.start()


    def sendDataFromDevice(self,deviceName,deviceAddress,data,time):
        if deviceName ==str(self.device[0]) and deviceAddress == str(self.device[1]):
            msg = '{"messageID":"' + str(self.messageId) + '","type":"dataFromDevice" ' \
                ',"deviceName":"'+deviceName+'","deviceAddress":"'+deviceAddress+'","data":'+data+ ',"time":"' + str(time) +'"}'
            if not self.stopSender:
                self.send_udp_msg(msg)


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


    # def send_msg(self,msg):
    #     # Prefix each message with a 4-byte length (network byte order)
    #     self.messageId=self.messageId+1
    #     msg = struct.pack('>I', len(msg)) + str.encode(msg)
    #     self.udpSocket.sendto(msg,self.clientAddress)
    #     print("sent message ",msg)

    def send_udp_msg(self,msg):
        self.udpSocket.sendto(msg.encode(), (str(self.clientAddress[0]), int(self.clientAddress[1])))
        #print("sent message to cient ",msg)


    def receiver(self):
        print("receiver started ",self)
        exceptionsCounter=0
        while True:
            if self.stopReceiver:
                print("exiting receiver ",self)
                self.stopChecker = True
                self.stopSender = True
                return
            try:
                data, addr = self.udpSocket.recvfrom(4096)
                if data is not None:
                    self.interpretMessage(bytes.decode(data))
                    exceptionsCounter=0
            except Exception as e:
                exceptionsCounter+=1
                print("client receiver exception that sets stopSender = True ",exceptionsCounter, e)
                if exceptionsCounter>50:
                    self.stopSender= True
                    self.stopReceiver = True
                    self.stopChecker =True


    def keepaliveSender(self):
        print("starting sender ",self)
        while True:
            if self.stopSender:
                self.stopChecker = True
                self.stopReceiver = True
                print("exiting sender ",self)
                return
            self.send_udp_msg("k!e@e#p$a%l^i&v*e(")
            print("sent keepalive and i'm ", self)
            time.sleep(2)


    def moduleChecker(self):
        while True:
            if self.moduleDisconnected:
                self.stopSender=True
                self.stopReceiver=True
                self.send_udp_msg("ERROR: Module disconnected")
                print("module disconnected")
                return
            if self.stopChecker:
                print("exiting module checker", self)
                return


    def interpretMessage(self,data):
        if data == "k!e@e#p$a%l^i&v*e(":
            pass
        elif data=="c!l@i#e$n%t^s&t*o(p)":
            print("received clientstop i'm " ,self)
            self.stopSender=True
            self.stopReceiver = True
            self.stopChecker=True
        else:
            try:
                self.currentModule.sendDataToDevice(self.device, data)
            except Exception as e:
                print("error in client message interpreter ",e)
