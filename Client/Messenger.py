import json
import socket
import time
import multiprocessing as mp
import struct
class Messenger:
    socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    add=""
    #result={}
    receiverProcess=mp.Process
    senderProcess=mp.Process
    messageId = 0
    def __init__(self,conn,add):
        #self.result={"ID":-1}
        self.socket=conn
        self.add=add
        #self.receiverProcess = mp.Process(target=self.receiver, args=())
        #self.senderProcess = mp.Process(target=self.sender, args=())
        #self.receiverProcess.start()
        #self.senderProcess.start()


    # def handleAuthentication(self,data):
    #     if data["response"]=="access_granted":
    #         self.access=True


    def sendLoginRequest(self,login,password):
        msg='{"ID":"'+str(self.messageId)+'","type":"authRequest","login":"'+login+'","password":"'+password+'"}'
        self.send_msg(msg)
        result = self.getResult()
        return result

    def askForDevices(self):
        msg = '{"ID":"' + str(
            self.messageId) + '","type":"devicesRequest"}'
        self.send_msg(msg)
        result = self.getResult()
        return result

    def askForConnectionToDevice(self,device):
        msg = '{"ID":"' + str(
            self.messageId) + '","type":"deviceConnectionRequest","device":"' + device + '"}'
        self.send_msg(msg)
        result = self.getResult()
        return result


    def getResult(self):
        try:
            print("gettingResult")
            data=bytearray.decode(self.recv_msg())
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
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def send_msg(self,msg):
        # Prefix each message with a 4-byte length (network byte order)
        self.messageId=self.messageId+1
        msg = struct.pack('>I', len(msg)) + str.encode(msg)
        self.socket.sendall(msg)
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

    # def receiver(self):
    #     try:
    #         print("receiver started")
    #         while True:
    #             data=bytearray.decode(self.recv_msg())
    #             self.interpretMessage(data)
    #     except Exception as e:
    #         print(e)

    # def sender(self):
    #     print("sender started")
    #     while True:
    #         self.socket.sendall("elo".encode())
    #         print(self.socket)
    #         time.sleep(5)

if __name__ == '__main__':
    sockrecv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockrecv.bind(('localhost',1101))
    sockrecv.listen()
    conn,add=sockrecv.accept()
    messenger=Messenger(conn,add)