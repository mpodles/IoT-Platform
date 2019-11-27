import json
import socket
import time
import multiprocessing as mp
import threading as thr
import struct

class BridgeMessenger:
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bridgeAddress=None
    messageId = 0
    stopSender=False

    def __init__(self,udpSocket,bridgeAddress=""):
        self.udpSocket = udpSocket
        self.bridgeAddress=bridgeAddress
        self.senderThread = thr.Thread(target=self.keepaliveSender, args=())
        self.senderThread.start()


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
            packet,addr = self.udpSocket.recvfrom(n - len(data))
            print(packet,"  ",addr)
            self.bridgeAddress=addr
            if not packet:
                return None
            data.extend(packet)
        return data

    def send_udp_msg(self, msg):
        # Prefix each message with a 4-byte length (network byte order)
        #self.messageId = self.messageId + 1
        #msg = struct.pack('>I', len(msg)) + str.encode(msg)
        if self.bridgeAddress !="":
            self.udpSocket.sendto(msg.encode(),self.bridgeAddress)
            print("sent message ", msg)
        else:
            print("bridge address undefined")


    def constructMessage(self,data):
        data["messageID"]=self.messageId
        msg=json.dumps(data)
        return msg

    # def receiver(self):
    #     global clientsMessengers
    #     global bridgesMessengers
    #     try:
    #         print("receiver started")
    #         while True:
    #             data = self.recv_msg()
    #             if data is not None:
    #                 self.interpretMessage(bytearray.decode(data))
    #     except Exception as e:
    #         print(e)



    def keepaliveSender(self):
        while True:
            if self.stopSender :
                print("exiting sender")
                return
            self.send_udp_msg("k!e@e#p$a%l^i&v*e(")
            time.sleep(2)

    def receive_old(self):
        global clientsMessengers
        global bridgesMessengers
        try:
            while True:
                data = self.recv_msg()
                if data is not None:
                    print(data)
                    return bytearray.decode(data)
        except Exception as e:
            print(e)

    def receive(self):
        global clientsMessengers
        global bridgesMessengers
        while True:
            data, addr = self.udpSocket.recvfrom(4096)
            self.bridgeAddress = addr
            if data is not None:
                return bytes.decode(data)




class ServerMessenger:
    tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    seenAs=""
    #result={}
    receiverProcess=mp.Process
    senderProcess=mp.Process
    messageId = 0
    def __init__(self,tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM),udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)):
        #self.result={"ID":-1}
        self.tcpSocket=tcpSocket
        self.udpSocket=udpSocket
        #self.seenAs=seenAs
        #self.senderThread= thr.Thread(target=self.sender)
        #self.senderThread.start()
        #self.receiverProcess = mp.Process(target=self.receiver, args=())
        #self.senderProcess = mp.Process(target=self.sender, args=())
        #self.receiverProcess.start()
        #self.senderProcess.start()


    # def handleAuthentication(self,data):
    #     if data["response"]=="access_granted":
    #         self.access=True


    def sendAuthorizationRequest(self,login,password):
        msg='{"messageID":"'+str(self.messageId)+'","type":"authorizationRequest","login":"'+str(login)+'","password":"'+str(password)+'"}'
        self.send_msg(msg)
        result = self.getResult()
        return result

    def askForBridges(self,userID):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"bridgesRequest","userID":"'+str(userID)+'"}'
        self.send_msg(msg)
        result = self.getResult()
        return result

    def askForBridgesDevices(self,bridgeID):
        msg = '{"messageID":"' + str(
            self.messageId) + '","type":"devicesRequest","bridgeID":"'+str(bridgeID)+'"}'
        self.send_msg(msg)
        result = self.getResult()
        return result

    def askForConnectionToDevice(self,device,behindNat,socketAddress=""):
        if behindNat:
            msg = '{"messageID":"' + str(self.messageId) + '","type":"deviceConnectionRequest","deviceID":"' + str(device) + '","behindNat":"'+str(behindNat)+'"}'
        else:
            msg = '{"messageID":"' + str(self.messageId) + '","type":"deviceConnectionRequest","deviceID":"' + str(
                device) + '","behindNat":"' + str(behindNat) + '","clientAddress":"'+socketAddress+'"}'
        self.send_msg(msg)
        result = self.getResult()
        return result


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

    # def interpretMessage(self, data):
    #     print("received", data)
    #     parsedData = json.loads(data)
    #     print(parsedData)
    #     self.result= parsedData
    #     # msgType = parsedData["type"]
    #     # if msgType == "authResponse":
    #     #     self.handleAuthentication(parsedData)
    #     # elif msgType == "":
    #     #     pass

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

    def receive(self):
        global clientsMessengers
        global bridgesMessengers
        try:
            print("receiver started")
            while True:
                data=self.recv_msg()
                if data is not None:
                    return bytearray.decode(data)
        except Exception as e:
            print(e)


    def sender(self):
        print("sender started")
        while True:
            self.udpSocket.sendto(("keepalive connected as"+self.seenAs).encode(),('localhost', 1101))
            time.sleep(2)

if __name__ == '__main__':
    msg=ServerMessenger(2,3)
    msg.sender()