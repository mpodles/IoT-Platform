import time

import Bridge.Messenger as msg
import Bridge.Device as dev
import Bridge.Options as opt



devices= [dev.Device("device1","blabla","rfidreader"),dev.Device("device2","blabla2","rfidwriter"),dev.Device("device3","bsdfabla","rfid")]
options=[opt.Options("rfidreader",["read"]),opt.Options("rfidwriter",["write"]),opt.Options("rfid",["read","write"])]
device =dev.Device("device1","blabla","rfidreader")
data= 30

msg.connectToBridge()
msg.registerDevices(devices)
time.sleep(300)
#msg.registerOptions(options)
#msg.sendDataFromDevice(device,data)
#while True:
#    data=msg.getData()
#    print()
