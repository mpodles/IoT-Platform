import kivy

import Client.Connector as conn
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from multiprocessing import freeze_support


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = GridLayout()
        layout.cols = 2
        layout.add_widget(Label(text='User Name1'))
        self.username = TextInput(multiline=False, width=500)
        self.username.text="elo"
        layout.add_widget(self.username)
        layout.add_widget(Label(text='password1'))
        self.password = TextInput(password=True, multiline=False)
        layout.add_widget(self.password)
        loginButtonObj =Button(text='login1')
        loginButtonObj.bind(on_press=self.loginButton)
        layout.add_widget(loginButtonObj)
        connectButtonObj = Button(text='connect to server')
        connectButtonObj.bind(on_press=self.connectButton)
        layout.add_widget(connectButtonObj)
        self.add_widget(layout)

    def makePopup(self,title,text):
        popuplayout = GridLayout()
        popuplayout.cols = 1
        popuplayout.add_widget(Label(text=text))
        closeButton = Button(text='close')
        popuplayout.add_widget(closeButton)
        popup = Popup(title=title, content=popuplayout)
        closeButton.bind(on_press=popup.dismiss)
        popup.open()

    def connectButton(self,button):
        try:
            conn.connectToServer()
            self.makePopup("info","Connected")
        except Exception as e:
            self.makePopup("error", str(e))

    def loginButton(self,button):
        result=conn.authenticate(self.username.text, self.password.text)
        if result:
            self.parent.current='screen2'
        else:
            self.makePopup("error", "login/password not found")
class RegularScreen(Screen):
    def __init__(self, **kwargs):
        super(RegularScreen, self).__init__(**kwargs)
        layout = GridLayout()
        layout.cols = 2
        layout.add_widget(Label(text='User Name2'))
        username = TextInput(multiline=False, width=500)
        layout.add_widget(username)
        layout.add_widget(Label(text='password2'))
        password = TextInput(password=True, multiline=False)
        layout.add_widget(password)
        layout.add_widget(Button(text='login2'))
        self.add_widget(layout)
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
        screenManager.current = 'screen1'
        return screenManager


if __name__=='__main__':
    freeze_support()
    IoTPlatformClientApp().run()