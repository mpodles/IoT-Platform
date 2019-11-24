import json
import socket
import time
import multiprocessing as mp
import struct
import Server.DatabaseConnection as dbc
import Server.UDPServer
import Server.Messengers as messengers



class Messenger:
    socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    add=""
    messageId = 0
    receiverProcess=mp.Process
    #senderProcess=mp.Process
    def __init__(self,conn,add):
        # if type=="bridge":
        #     global bridgesMessengers
        #     bridgesMessengers[add]=self
        #
        # elif type =="client":
        #     global clientsMessengers
        #     clientsMessengers[add]=self
        #     print(clientsMessengers)
        self.socket=conn
        self.add=add
        self.receiverProcess = mp.Process(target=self.receiver, args=())
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
            self.handleAuthorization(parsedData)
        elif msgType == "bridgesRequest":
            self.handleBridgesRequest(parsedData)
        elif msgType == "devicesRequest":
            self.handleDevicesRequest(parsedData)
        elif msgType == "devicesConnectionRequest":
            self.handleDevicesConnectionRequest(parsedData)
        elif msgType== "registrationRequest":
            self.handleBridgesRegistration(parsedData)

    def handleBridgesRegistration(self,data):
        data

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
        deviceID,behindNat=data["deviceID"],data["behindNat"]
        result = dbc.select("Devices", rows="*", condition='WHERE DeviceID="' + deviceID +'"')
        if result.__len__() > 0:
            deviceAddress= result[0][1]
            deviceName= result[0][2]
            bridgeID =result[0][3]
            requestToBridgeDictToJson = {"type":"devicesConnectionRequest","deviceName":str(deviceName),"deviceAddress":str(deviceAddress)}
            req=bridgesMessengers[result[0][1]].constructMessage(requestToBridgeDictToJson)  # TODO
            bridgesMessengers[result[0][3]].send_msg(req)
            #dictionaryToJson = {"type": "devicesConnectionResponse", "response": }
        else:
            dictionaryToJson={"type":"devicesConnectionResponse","response":"deviceNotFound"}
        msg=self.constructMessage(dictionaryToJson)
        self.send_msg(msg)

    def handleAuthorization(self,data):
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
        try:
            print("receiver started")
            while True:
                data=self.recv_msg()
                if data is not None:
                    print(self)
                    print(messengers.clientsMessengers)
                    self.interpretMessage(bytearray.decode(data))
        except Exception as e:
            print(self)
            print(messengers.clientsMessengers)
            if self in messengers.clientsMessengers.values():
                print("found self in clients")
            #elif self in bridgesMessengers.values():
                #print("found self in bridges")
                #del bridgesMessengers

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
    socksend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socksend.connect(('localhost', 1101))
    messenger=Messenger(socksend,socksend.getpeername())
