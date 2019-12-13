import time

import Bridge.Messenger as msg
import Bridge.DeviceTODELETE as dev
import Bridge.OptionsTODELETE as opt



devices= [dev.Device("device1","blabla","rfidreader"),dev.Device("device2","blabla2","rfidwriter"),dev.Device("device3","bsdfabla","rfid")]
options=[opt.Options("rfidreader",["read"]),opt.Options("rfidwriter",["write"]),opt.Options("rfid",["read","write"])]
device =dev.Device("device1","blabla","rfidreader")
option=[opt.Options("rfidreader",["read"])]
data= 30

def on_option(option,data):
    print("REACHED RFID ON OPTION ",option," ",data)

def on_data(data):
    print ("REACHED RFID ON DATA ",data)

msg.connectToBridge()
msg.registerDevices(devices)
msg.registerOptions(options)
msg.bind(device=device,on_data=on_data,on_option=on_option)
i=0
while True:
    time.sleep(3)
    msg.sendDataFromDevice(device,data+i)
    i+=7
#while True:
#    data=msg.getData()
#    print()
