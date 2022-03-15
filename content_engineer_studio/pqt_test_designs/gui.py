from textwrap import shorten
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.config import Config

from utils.excel_helpers import *


class MyGrid(GridLayout):
    pass


class MyScrollView(ScrollView):
    pass


class Sidebar(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load Excel file
        df = excel.load("sample.xlsx", "Sheet1")
        excel.incomplete(df)
        for i, row in df.iterrows():
            size = dp(25)
            if row["bool_check"] == 1:
                b = Button(
                    text=str(i + 1),
                    size_hint=(None, None),
                    background_color=(1.70, 1.45, 0.57, 1),
                    size=(size, size),
                )
                self.add_widget(b)
            else:
                b = Button(
                    text=str(i + 1),
                    size_hint=(None, None),
                    background_color=(0.43, 0.74, 1.11, 1),
                    size=(size, size),
                )
                self.add_widget(b)


class Chat(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load Excel file
        df = excel.load("sample.xlsx", "Sheet1")
        excel.incomplete(df)

        for i, row in df.iterrows():
            b = Button(text=str(row["Name"]), size_hint=(1, None))
            # b._label.refresh()
            # print(b._label.texture.size)
            # b = Label(text=str(row['Name']),
            #     shorten=(True),
            #     font_size=("20sp"),
            #     size_hint=(None, None),
            #     size=(b._label.texture.size))
            self.add_widget(b)

        # # Construct layout
        # csize = dp(100)
        # for i, row in df.iterrows():

        #     if row['bool_check'] == 1:
        #         b = Button(text=str(row['Name']),
        #                 size_hint=(1, None),
        #                 background_color =(1.31, 1.26, 1.77, 5))
        #     else:
        #         b = TextInput(text=str(row['Name']),
        #                 size_hint=(1, None),
        #                 background_color =(.8, .8, .8, 1))
        #     self.add_widget(b)
        #
        #         for i, row in df.iterrows():
        # b = Label(text=str(row['Name']))
        # b._label.refresh()
        # print(b._label.texture.size)
        # b = Label(text=str(row['Name']),
        #     shorten=(True),
        #     font_size=("20sp"),
        #     size_hint=(None, None),
        #     size=(b._label.texture.size))


class MainWindow(Screen):
    pass


class Options(Screen):
    pass


class Help(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my.kv")


class MyApp(App):  # <- Main Class
    def build(self):
        Window.size = (1200, 500)
        Window.left = 0
        Window.top = 640
        return kv


if __name__ == "__main__":
    MyApp().run()
