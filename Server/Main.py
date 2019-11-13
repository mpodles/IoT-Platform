import logging
import socket
import sys
import multiprocessing as mp
import time
from util import *
import Server.DatabaseConnection as dc


def listenForBridges():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.1.26', 1100))
    sock.listen()
    print("Bridges socket listening")
    conn, add = sock.accept()
def listenForClients():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost',1101))
    sock.listen()
    while True:
        print("Clients socket listening")
        time.sleep(1)
    conn,add =sock.accept()
    handleClient(conn,add)
def handleClient(conn,add):
    dataRec=bytes.decode(conn.recv(1024))
    dataBase=dc.select(rows="UserID",table="Users",condition="WHERE")
    conn.sendall(str.encode(str()))
    time.sleep(20)
def handleBridge(conn,add):
    pass
def sendNotification():
    pass
def helpWithConnection():
    pass


if __name__ == '__main__':
    clientsProcess = mp.Process(target=listenForClients, args=())
    while True:
        print("dupsko")
        time.sleep(1)
    #clientsProcess.daemon = True
    clientsProcess.start()
    bridgesProcess = mp.Process(target=listenForBridges, args=())
    #bridgesProcess.daemon = True
    bridgesProcess.start()
