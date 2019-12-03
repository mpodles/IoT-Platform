import time

import Bridge.Messenger as msg
import Bridge.Device as dev
import Bridge.Options as opt



devices= [dev.Device("deviceadd1","devicename1"),dev.Device("deviceadd2","devicename2","ble"),dev.Device("deviceadd3","devicename3","ble")]
options=[opt.Options("ble",["read","write","subscribe"])]
device =dev.Device("deviceadd1","devicename1","ble")
device2 =dev.Device("deviceadd3","devicename3","ble")
data= 30

def on_option(option,data):
    print("REACHED BLE ON OPTION ",option," ",data)

def on_data(data):
    print ("REACHED BLE ON DATA ",data)

def on_option2(option,data):
    print("REACHED BLE ON OPTION2 ",option," ",data)

def on_data2(data):
    print ("REACHED BLE ON DATA2 ",data)


msg.connectToBridge()
msg.registerDevices(devices)
msg.registerOptions(options)
msg.bind(device=device,on_data=on_data,on_option=on_option)
msg.bind(device=device2,on_data=on_data2,on_option=on_option2)
i=0
while True:
    time.sleep(1)
    msg.sendDataFromDevice(device,data+i)
    msg.sendDataFromDevice(device2, data + 2*i)
    i+=15
#while True:
#    data=msg.getData()
#    print()
