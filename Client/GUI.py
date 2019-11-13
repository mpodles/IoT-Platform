import kivy

import Client.Connector as conn
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

connector=conn.Connector

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = GridLayout()
        layout.cols = 2
        layout.add_widget(Label(text='User Name1'))
        self.username = TextInput(multiline=False, width=500)
        layout.add_widget(self.username)
        layout.add_widget(Label(text='password1'))
        self.password = TextInput(password=True, multiline=False)
        layout.add_widget(self.password)
        loginButtonObj =Button(text='login1')
        loginButtonObj.bind(on_press=self.loginButton)
        layout.add_widget(loginButtonObj)
        self.add_widget(layout)

    def loginButton(self,button):
        connector.authenticate(self.username, self.password)
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

screenManager=ScreenManager()
screenManager.add_widget(LoginScreen(name='screen1'))
screenManager.add_widget(RegularScreen(name='screen2'))
screenManager.add_widget(ConnectedScreen(name='screen3'))
screenManager.current='screen1'
class IoTPlatformClientApp(App):
    def build(self):
        return screenManager

if __name__=='__main__':
    IoTPlatformClientApp().run()