import kivy
import time

import Client.Connector as conn
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.text import  Label as CoreLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from multiprocessing import freeze_support
import threading as thr
from kivy.clock import Clock
from functools import partial
import json


sessionLogin=""
sessionPassword=""
def makePopup(title,text):
        popuplayout = GridLayout()
        popuplayout.cols = 1
        popuplayout.add_widget(Label(text=text))
        closeButton = Button(text='close')
        popuplayout.add_widget(closeButton)
        popup = Popup(title=title, content=popuplayout)
        closeButton.bind(on_press=popup.dismiss)
        popup.open()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.isConnected = False
        Window.size=500,300

        self.layout = GridLayout()
        self.layout.cols = 2

        self.usernameLabel=Label(text='User Name')

        self.usernameInput = TextInput(multiline=False)
        self.usernameInput.text="mietek"

        self.passwordLabel = Label(text='Password')

        self.passwordInput = TextInput(password=True, multiline=False)
        self.passwordInput.text="elo"

        self.loginButton =Button(text='Login')
        self.loginButton.bind(on_press=self.login)

        self.connectButton = Button(text='connect to server')
        self.connectButton.bind(on_press=self.connect)

        self.layout.add_widget(self.usernameLabel)
        self.layout.add_widget(self.usernameInput)
        self.layout.add_widget(self.passwordLabel)
        self.layout.add_widget(self.passwordInput)
        self.layout.add_widget(self.loginButton)
        self.layout.add_widget(self.connectButton)
        self.add_widget(self.layout)

    def connect(self,button):
        try:
            conn.connectToServer()
            makePopup("info","Connected")
            self.isConnected=True
        except Exception as e:
            makePopup("error", str(e))

    def login(self,button):
        if self.isConnected:
            result=conn.authorizate(self.usernameInput.text, self.passwordInput.text)
            if result:
                self.parent.current='screen2'
                self.parent.screens[1].sessionLogin=self.usernameInput.text
                self.parent.screens[1].sessionPassword = self.passwordInput.text
                self.parent.screens[1].userID = result
                Window.size=1000,800
            else:
                self.makePopup("error", "login/password not found")
        else:
            makePopup("error","not connected to server")



class RegularScreen(Screen):
    #viewProp = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RegularScreen, self).__init__(**kwargs)
        self.sessionLogin=""
        self.sessionPassword=""
        self.userID=0
        self.bridges=[]
        self.devices={}
        #Window.bind(on_resize=self.resize)


        self.layout=BoxLayout()
        self.layout.orientation="vertical"
        self.layout.size_hint_y=None

        self.menu = GridLayout()
        self.menu.cols =3
        self.menu.size =(Window.width, Window.height/10)
        self.menu.size_hint=None,None

        self.bridgesSpinner = Spinner()
        self.bridgesSpinner.values = []
        self.bridgesSpinner.text = "Choose your bridge"
        self.bridgesSpinner.size_hint = None,None
        self.bridgesSpinner.size = (Window.width*3/5, Window.height * 1 / 10)
        self.bridgesSpinner.pos_hint = {'x': 0, 'y': 0}
        self.bridgesSpinner.bind(text=self.bridgeChange)

        self.dataButton = Button(text="Get\ndata")
        self.dataButton.size_hint=None,None
        self.dataButton.size = (Window.width/5,Window.height*1/10)
        self.dataButton.bind(on_press=self.getDataForUser)


        self.natToogle = ToggleButton(text="I'm behind\n NAT")
        self.natToogle.state ='down'
        self.natToogle.size_hint=None,None
        self.natToogle.size = (Window.width/5,Window.height*1/10)

        self.devicesLayout = ScrollView()
        #self.devicesLayout.id =self.viewProp
        self.devicesLayout.size_hint=None,None
        self.devicesLayout.size =(Window.width, Window.height*9/10)
        #self.devicesLayout.height=40

        self.devicesList = GridLayout()
        self.devicesList.cols=1
        self.devicesList.size =(Window.width, Window.height)
        self.devicesList.size_hint=None,None
        self.devicesList.bind(minimum_height=self.devicesList.setter("height"))


        self.menu.add_widget(self.bridgesSpinner)
        self.menu.add_widget(self.dataButton)
        self.menu.add_widget(self.natToogle)

        self.devicesLayout.add_widget(self.devicesList)

        self.layout.add_widget(self.menu)
        self.layout.add_widget(self.devicesLayout)
        self.add_widget(self.layout)


    def bridgeChange(self,spinner,text):
        self.devicesList.clear_widgets()
        try:
            devices=self.devices[text]
            for device in devices:
                devicesRow = GridLayout()
                devicesRow.size_hint_y = None
                devicesRow.cols = 2
                info = Label(text=("ID: "+str(device[0])+"   Address: "+str(device[1])+"\n Name: "+str(device[2])+"\n Type: "+str(device[3])), size=(Window.width * 3 / 5, 90), size_hint=(None, None))
                connectButton = Button(text="Connect", size=(Window.width* 2/ 5, 90), size_hint=(None, None))
                connectButton.bind(on_press=self.connectToDevice)
                devicesRow.add_widget(info)
                devicesRow.add_widget(connectButton)
                self.devicesList.add_widget(devicesRow)
        except Exception as e:
            print("Error changing bridge ",e)



    def getDataForUser(self,button):
        result=conn.getBridgesForUser(self.userID)
        self.bridgesSpinner.values = []
        for bridge in result:
            self.bridges.append(bridge)
            devices=conn.getDevicesForBridge(bridge[0])
            self.devices["Address: "+str(bridge[2])+"\n Name: "+str(bridge[3])]=devices
            self.bridgesSpinner.values.append("Address: "+str(bridge[2])+"\n Name: "+str(bridge[3]))
        self.bridgesSpinner.text = "Choose your bridge"


    def connectToDevice(self,button):
        for child in button.parent.children:
            if not isinstance(child, Button):
                infoLabel=child
        print(infoLabel.text)
        tmp=infoLabel.text.split("   Address: ")
        deviceID=tmp[0][4:]
        tmp=tmp[1].split("\n Name: ")
        deviceAddress=tmp[0]
        tmp = tmp[1].split("\n Type: ")
        deviceName=tmp[0]
        deviceType=tmp[1]
        behindNat = False
        if self.natToogle.state =='down':
            behindNat=True
        messenger,options=None,None
        try:
            messenger,options=conn.connectToDevice(deviceID,behindNat)
        except Exception as e:
            makePopup("Error",str(e))
            return
        self.parent.screens[2].options=options
        self.parent.screens[2].connectedDevice=(deviceID,deviceAddress,deviceName,deviceType)
        self.parent.screens[2].messenger =messenger
        self.parent.screens[2].buildButtons()
        self.parent.screens[2].stopFlag = False
        self.parent.screens[2].textLabel.text = ""
        self.parent.screens[2].receiverThread= thr.Thread(target=self.parent.screens[2].getDataFromMessenger)
        self.parent.screens[2].receiverThread.start()
        self.parent.current="screen3"
        #Clock.schedule_interval(self.parent.screens[2].getDataFromMessenger, 1)


    # def resize(self,me,x_size,y_size):
    #     self.devicesLayout.size=Window.width,Window.height*9/10
    #     self.menu.size = Window.width, Window.height * 1 / 10
    #     self.bridgesSpinner.size=Window.width*3/5,Window.height*1/10
    #     self.dataButton.size=Window.width*1/5,Window.height*1/10
    #     self.natToogle.size = Window.width * 1 / 5, Window.height * 1 / 10
    #     for row in self.devicesList.children:
    #         for child in row.children:
    #             if isinstance(Button,child):
    #                 child.size= Window.width*2/5,90
    #             else:
    #                 child.size = Window.width *3/ 5, 90
class ConnectedScreen(Screen):
    def __init__(self, **kwargs):
        super(ConnectedScreen, self).__init__(**kwargs)
        self.messenger=None
        self.receiverThread= None
        self.stopFlag=True
        self.options =None
        self.connectedDevice=""
        self.layout=GridLayout()
        self.layout.rows=3

        self.disconnectButton=Button(text="disconnect")
        self.disconnectButton.size=Window.width,Window.height/20
        self.disconnectButton.size_hint=1,None
        self.disconnectButton.bind(on_press=self.disconnect)

        self.textField=ScrollView()
        self.textField.size=Window.width,Window.height*7/10
        self.textField.size_hint=1,None

        self.textLabel=Label(text=""*100,valign='bottom')
        self.textLabel.text_size=Window.width,Window.height
        self.textLabel.size=Window.width,self.textLabel.text_size[1]
        self.textLabel.size_hint=1,None

        self.menu=GridLayout()
        self.menu.rows=2

        self.textInput=TextInput()

        self.buttons=GridLayout()
        self.buttons.rows=1

        self.menu.add_widget(self.buttons)
        self.menu.add_widget(self.textInput)

        self.textField.add_widget(self.textLabel)

        self.layout.add_widget(self.disconnectButton)
        self.layout.add_widget(self.textField)
        self.layout.add_widget(self.menu)

        self.add_widget(self.layout)


    def disconnect(self,button):
        self.stopFlag=True #stop receiving
        conn.disconnectFromBridge() #tell messenger to send disconnect info and stop sending keepalives
        self.messenger=None #delete messenger
        time.sleep(2) #wait for server to update
        self.parent.current = "screen2"
        if button == 'error':
            self.parent.screens[1].getDataForUser("no button")#get data again


    def getDataFromMessenger(self):
        while True:
            if self.stopFlag:
                return
            try:
                data=self.messenger.receive()
            except Exception as e:
                print("bridge receiver error",e)
                makePopup("Error", "Lost bridge connection")
                self.disconnect("error")
            data=self.interpretData(data)
            if data is not None:
                self.textLabel.text += "\n Received from ("+str(self.connectedDevice[1])+" , "+self.connectedDevice[2]+"): " + str(data)
                self.textField.scroll_to(self.textInput)


    def interpretData(self,data):
        if data =='k!e@e#p$a%l^i&v*e(':
            return None
        elif data=="ERROR: Module disconnected":
            makePopup("Error", "Module with device disconnected")
            self.disconnect("error")
            return None
        else:
            parsedData=json.loads(data)
            deviceName=parsedData["deviceName"]
            deviceAddress=parsedData["deviceAddress"]
            if self.connectedDevice[1]==deviceAddress and self.connectedDevice[2]==deviceName:
                return parsedData["data"]

    def sendMessage(self,button):
        self.textLabel.text+="\n Sent: "+self.textInput.text
        dictionaryToJson = {"type": "consoleMessage","deviceAddress":self.connectedDevice[1], "deviceName": self.connectedDevice[2],"payload":self.textInput.text}
        msg = self.messenger.constructMessage(dictionaryToJson)
        self.messenger.send_udp_msg(msg)
        self.textInput.text=""
        self.textField.scroll_to(self.textInput)

    def buildButtons(self):
        self.buttons.clear_widgets()
        self.sendButton = Button(text="send")
        self.sendButton.bind(on_press=self.sendMessage)
        self.buttons.add_widget(self.sendButton)
        for option in self.options:
            customButton = Button(text=str(option))
            customButton.bind(on_press=self.customButton)
            self.buttons.add_widget(customButton)

    def customButton(self,button):
        command=button.text
        self.textLabel.text += '\n Sent command "'+command+'": ' + self.textInput.text
        dictionaryToJson = {"type": "consoleCommand", "command":command,"deviceAddress": self.connectedDevice[1],
                            "deviceName": self.connectedDevice[2], "payload": self.textInput.text}
        msg = self.messenger.constructMessage(dictionaryToJson)
        self.messenger.send_udp_msg(msg)
        self.textInput.text = ""
        self.textField.scroll_to(self.textInput)


class IoTPlatformClientApp(App):
    def build(self):
        self.screenManager = ScreenManager()
        self.loginScreen=LoginScreen(name='screen1')
        self.regularScreen=RegularScreen(name='screen2')
        self.connectedScreen=ConnectedScreen(name='screen3')
        self.screenManager.add_widget(self.loginScreen)
        self.screenManager.add_widget(self.regularScreen)
        self.screenManager.add_widget(self.connectedScreen)
        self.screenManager.current = 'screen1'

        Window.bind(on_resize=self.resize)

        return self.screenManager

    def resize(self,me,x_size,y_size):

        self.regularScreen.devicesLayout.size=Window.width,Window.height*9/10
        self.regularScreen.menu.size = Window.width, Window.height * 1 / 10
        self.regularScreen.bridgesSpinner.size=Window.width*3/5,Window.height*1/10
        self.regularScreen.dataButton.size=Window.width*1/5,Window.height*1/10
        self.regularScreen.natToogle.size = Window.width * 1 / 5, Window.height * 1 / 10
        for row in self.regularScreen.devicesList.children:
            for child in row.children:
                if isinstance(child,Button):
                    child.size= Window.width*2/5,90
                else:
                    child.size = Window.width *3/ 5, 90

        self.connectedScreen.disconnectButton.size=Window.width,Window.height/20
        self.connectedScreen.textField.size=Window.width,Window.height*7/10
        self.connectedScreen.textLabel.text_size=Window.width,Window.height
        self.connectedScreen.textLabel.size = Window.width, self.connectedScreen.textLabel.text_size[1]




if __name__=='__main__':
    freeze_support()
    IoTPlatformClientApp().run()