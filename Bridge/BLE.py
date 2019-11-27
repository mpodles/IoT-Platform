import time

import Bridge.Messenger as msg
import Bridge.Device as dev
import Bridge.Options as opt



devices= [dev.Device("deviceadd1","devicename1","ble"),dev.Device("deviceadd2","devicename2","ble"),dev.Device("deviceadd3","devicename3","ble")]
options=[opt.Options("ble",["read","write","subscribe"])]
device =dev.Device("deviceadd1","devicename1","ble")
data= 30

def on_option(option,data):
    print(options," ",data)

def on_data(data):
    print (data)

msg.connectToBridge()
msg.registerDevices(devices)
msg.registerOptions(options)
#msg.bindDevice(device=device,on_data=on_data,on_option=on_option)
i=0
while True:
    time.sleep(3)
    msg.sendDataFromDevice(device,data+i)
    i+=15
#while True:
#    data=msg.getData()
#    print()
