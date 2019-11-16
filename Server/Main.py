import logging
import socket
import sys
import multiprocessing as mp
import time
import Server.Messenger as msg
from util import *
import Server.DatabaseConnection as dc



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
    messengers = []
    while True:
        conn, add = sock.accept()
        newClientMessenger = msg.Messenger(conn, add)
        messengers.append(newClientMessenger)
        print(messengers)
def listenForClients():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost',1101))
    sock.listen()
    messengers=[]
    while True:
        conn, add = sock.accept()
        newClientMessenger = msg.Messenger(conn, add)
        messengers.append(newClientMessenger)
        print(messengers)

def sendNotification():
    pass
def helpWithConnection():
    pass


if __name__ == '__main__':
    clientsProcess = mp.Process(target=listenForClients, args=())
    #clientsProcess.daemon = True
    clientsProcess.start()
    bridgesProcess = mp.Process(target=listenForBridges, args=())
    #bridgesProcess.daemon = True
    bridgesProcess.start()
