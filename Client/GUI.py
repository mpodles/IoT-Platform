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
        Window.bind(on_resize=self.resize)


        self.layout=BoxLayout()
        self.layout.orientation="vertical"
        self.layout.size_hint_y=None

        self.menu = GridLayout()
        self.menu.cols =3
        self.menu.size =(Window.width, Window.height/10)
        self.menu.size_hint=None,None

        self.bridgesSpinner = Spinner()
        self.bridgesSpinner.values = ["3", "2", "2", "2", "2", "1", "2", "2", "2", "2", "1", "2", "2", "2", "2"]
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

        for i in range(25):
            devicesRow = GridLayout()
            devicesRow.size_hint_y=None
            devicesRow.cols = 3
            a=Label(text="elo"+str(i), size=(Window.width*3/5, 90), size_hint=(None, None))
            b=Button(text="Connect\n"+str(i+1), size=(Window.width/5, 90), size_hint=(None, None))
            c=Button(text="Subscribe\n"+str(i+2), size=(Window.width/5, 90), size_hint=(None, None))
            devicesRow.add_widget(a)
            devicesRow.add_widget(b)
            devicesRow.add_widget(c)
            self.devicesList.add_widget(devicesRow)

        self.menu.add_widget(self.bridgesSpinner)
        self.menu.add_widget(self.dataButton)
        self.menu.add_widget(self.natToogle)

        self.devicesLayout.add_widget(self.devicesList)

        self.layout.add_widget(self.menu)
        self.layout.add_widget(self.devicesLayout)
        self.add_widget(self.layout)


    def bridgeChange(self,spinner,text): #TODO
        self.devicesList.clear_widgets()
        devices=self.devices[text]
        for device in devices:
            devicesRow = GridLayout()
            devicesRow.size_hint_y = None
            devicesRow.cols = 3
            info = Label(text=device, size=(Window.width * 3 / 5, 90), size_hint=(None, None))
            connectButton = Button(text="Connect", size=(Window.width* 2/ 5, 90), size_hint=(None, None))
            devicesRow.add_widget(info)
            devicesRow.add_widget(connectButton)
            self.devicesList.add_widget(devicesRow)
        print(text)


    def resize(self,me,x_size,y_size):
        self.devicesLayout.size=Window.width,Window.height*9/10
        self.menu.size = Window.width, Window.height * 1 / 10
        self.bridgesSpinner.size=Window.width*3/5,Window.height*1/10
        self.dataButton.size=Window.width*1/5,Window.height*1/10
        self.natToogle.size = Window.width * 1 / 5, Window.height * 1 / 10
        for row in self.devicesList.children:
            for child in row.children:
                if isinstance(Button,child):
                    child.size= Window.width*2/5,90
                else:
                    child.size = Window.width *3/ 5, 90



    def getDataForUser(self,button): #TODO
        result=conn.getBridgesForUser(self.userID)
        bridges=result.getBridges() #TODO
        for bridge in bridges:
            devices=conn.getDevicesForBridge(bridge)

        self.bridgesSpinner.values=[result] #TODO


class ConnectedScreen(Screen):
    def __init__(self, **kwargs):
        super(ConnectedScreen, self).__init__(**kwargs)
        layout = GridLayout()
        layout.cols = 2
        layout.add_widget(Label(text='User Name3'))
        username = TextInput(multiline=False, width=500)
        layout.add_widget(username)
        layout.add_widget(Label(text='password3'))
        password = TextInput(password=True, multiline=False)
        layout.add_widget(password)
        layout.add_widget(Button(text='login3'))
        self.add_widget(layout)


class IoTPlatformClientApp(App):
    def build(self):
        screenManager = ScreenManager()
        screenManager.add_widget(LoginScreen(name='screen1'))
        screenManager.add_widget(RegularScreen(name='screen2'))
        screenManager.add_widget(ConnectedScreen(name='screen3'))
        screenManager.current = 'screen2'
        return screenManager


if __name__=='__main__':
    freeze_support()
    IoTPlatformClientApp().run()