import time

import API as api



devices= [api.Device("deviceadd1","devicename1"),api.Device("deviceadd2","devicename2","ble"),api.Device("deviceadd3","devicename3","ble")]
options=[api.Options("ble",["read","write","subscribe"])]
device =api.Device("deviceadd1","devicename1","ble")
device2 =api.Device("deviceadd3","devicename3","ble")
data= 30

def on_option(option,data):
    print("REACHED BLE ON OPTION ",option," ",data)

def on_data(data):
    print ("REACHED BLE ON DATA ",data)

def on_option2(option,data):
    print("REACHED BLE ON OPTION2 ",option," ",data)

def on_data2(data):
    print ("REACHED BLE ON DATA2 ",data)


api.connectToBridge()
api.registerDevices(devices)
api.registerOptions(options)
api.bind(device=device,on_data=on_data,on_option=on_option)
api.bind(device=device2,on_data=on_data2,on_option=on_option2)
i=0
while True:
    time.sleep(1)
    api.sendDataFromDevice(device,data+i)
    api.sendDataFromDevice(device2, data + 2*i)
    i+=15
    if i>2000:
        i=0
#while True:
#    data=msg.getData()
#    print()
