import kivy

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
        self.layout = GridLayout()
        self.layout.cols = 2
        self.layout.add_widget(Label(text='User Name1'))
        self.username = TextInput(multiline=False, width=500)
        self.username.text="mietek"
        self.layout.add_widget(self.username)
        self.layout.add_widget(Label(text='password1'))
        self.password = TextInput(password=True, multiline=False)
        self.password.text="elo"
        self.layout.add_widget(self.password)
        loginButtonObj =Button(text='login1')
        loginButtonObj.bind(on_press=self.loginButton)
        self.layout.add_widget(loginButtonObj)
        connectButtonObj = Button(text='connect to server')
        connectButtonObj.bind(on_press=self.connectButton)
        self.layout.add_widget(connectButtonObj)
        self.add_widget(self.layout)

    def connectButton(self,button):
        try:
            conn.connectToServer()
            makePopup("info","Connected")
        except Exception as e:
            makePopup("error", str(e))

    def loginButton(self,button):
        result=conn.authenticate(self.username.text, self.password.text)
        if result:
            self.parent.current='screen2'
            self.parent.screens[1].sessionLogin=self.username.text
            self.parent.screens[1].sessionPassword = self.password.text
            self.parent.screens[1].userID = result
        else:
            self.makePopup("error", "login/password not found")


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



    def getDataForUser(self,button):
        result=conn.getBridgesForUser(self.userID)
        self.bridgesSpinner.values = []
        for bridge in result:
            self.bridges.append(bridge)
            devices=conn.getDevicesForBridge(bridge[0])
            self.devices["Address: "+str(bridge[2])+"\n Name: "+str(bridge[3])]=devices
            self.bridgesSpinner.values.append("Address: "+str(bridge[2])+"\n Name: "+str(bridge[3]))


    def connectToDevice(self,button):
        for child in button.parent.children:
            if not isinstance(child, Button):
                infoLabel=child
        print(infoLabel.text)
        deviceID=infoLabel.text.split("   Address: ")[0][4:]
        behindNat = False
        if self.natToogle.state =='down':
            behindNat=True
        conn.connectToDevice(deviceID,behindNat)



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
        self.layout=GridLayout()
        self.layout.rows=2

        self.textField=ScrollView()
        self.textField.size=Window.width,Window.height*8/10
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

        self.sendButton=Button(text="send")
        self.sendButton.bind(on_press=self.sendMessage)

        self.otherButton1=Button(text="other1")
        self.otherButton2=Button(text="other2")

        self.buttons.add_widget(self.sendButton)
        self.buttons.add_widget(self.otherButton1)
        self.buttons.add_widget(self.otherButton2)

        self.menu.add_widget(self.buttons)
        self.menu.add_widget(self.textInput)

        self.textField.add_widget(self.textLabel)

        self.layout.add_widget(self.textField)
        self.layout.add_widget(self.menu)

        self.add_widget(self.layout)
        pass

    def sendMessage(self,button):
        self.textLabel.text+="\n Sent: "+self.textInput.text
        self.textInput.text=""
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

        self.connectedScreen.textField.size=Window.width,Window.height*8/10
        self.connectedScreen.textLabel.text_size=Window.width,Window.height
        self.connectedScreen.textLabel.size = Window.width, self.connectedScreen.textLabel.text_size[1]




if __name__=='__main__':
    freeze_support()
    IoTPlatformClientApp().run()