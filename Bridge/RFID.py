import time

import Bridge.Messenger as msg
import Bridge.Device as dev
import Bridge.Options as opt



devices= [dev.Device("device1","blabla","rfidreader"),dev.Device("device2","blabla2","rfidwriter"),dev.Device("device3","bsdfabla","rfid")]
options=[opt.Options("rfidreader",["read"]),opt.Options("rfidwriter",["write"]),opt.Options("rfid",["read","write"])]
device =dev.Device("device1","blabla","rfidreader")
option=[opt.Options("rfidreader",["read"])]
data= 30

def on_message(data):
    print (data)
msg.connectToBridge()
msg.registerDevices(devices)
msg.registerOptions(options)
#msg.bindDevice(device=device,on_message=on_message,options=option)
i=0
while True:
    time.sleep(3)
    msg.sendDataFromDevice(device,data+i)
    i+=15
#while True:
#    data=msg.getData()
#    print()
