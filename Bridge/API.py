import socket
from datetime import  datetime
import threading as thr
import json
import struct

messengerForModules=None

boundDevices=None

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
                else:
                    raise Exception("GOT NONE AS DATA")
            except Exception as e:
                print("bridge to module receiver exception", e)
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





class Device:
    address=""
    name=""
    type=""
    def __init__(self,address,name="",type=""):
        self.address=address
        self.name=name
        self.type=type

class Options:
    type=""
    options=[]
    def __init__(self,type,options):
        self.type=type
        self.options=options
