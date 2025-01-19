# TODO: Split this into multiple files

# pip install todoist-api-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
# ~/.credentials will need to be copied to wherever this is installed.

# If Google Calendar stops authenticating, go here:
#   https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html#getting-started
# and download the .json file to ~/.credentials and delete token.pickle.

#from todoist_api_python.api_async import TodoistAPIAsync
#from todoist_api_python.api import TodoistAPI
#import gkeepapi
#import platform
#import webcolors
#from gcsa.google_calendar import GoogleCalendar
#from gcsa.recurrence import Recurrence
#from functools import partial
from kivy.core.window import Window
#from kivy.factory import Factory
from kivymd.app import MDApp
#from kivy.graphics import Color, Line, RoundedRectangle
#from kivy.clock import Clock
#from kivy.uix.layout import Layout
#from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogSupportingText, MDDialogContentContainer
#from kivymd.uix.divider import MDDivider
#from kivymd.uix.label import MDLabel
#from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTrailingCheckbox, MDListItemSupportingText, MDListItemLeadingIcon
#from kivymd.uix.screen import MDScreen
#from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
#from kivymd.uix.widget import MDWidget
#from kivymd.uix.boxlayout import MDBoxLayout
#from kivymd.uix.button import MDButton, MDButtonText
#from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
#from kivy.app import App, ConfigParser
#from kivy.uix.button import Button
import sys
#from datetime import datetime, timedelta, date
#import pytz
import keyring
from screens.CalendarScreen import CalendarScreen
from screens.CookingScreen import CookingScreen
from screens.HomeScreen import HomeScreen
from screens.PrintScreen import PrintScreen
from agents.Lists import Lists
from agents.Notes import Notes

# Use keyring.set_password(service, email, password) to set the password
user_email = "aarondeno11@gmail.com"
google_oauth_key = keyring.get_password("google_oauth", user_email)
todoist_api_key = keyring.get_password("todoist_api", user_email)

#if platform.system() in ('Linux'):
#    start_format = "%-I:%M%p"
#else:
#    start_format = "%#I:%M%p"

class HomeDisplayApp(MDApp):
    def on_start(self):
        #self.fps_monitor_start()
        super(HomeDisplayApp, self).on_start()

    def build(self):
        Window.size=(1920, 1080)
        #Window.fullscreen = True
    #    cdl = self.root.ids.calendar_day_layout
    #    print(cdl)
    #    pass

    def on_switch_tabs(self, bar: MDNavigationBar, item: MDNavigationItem, item_icon: str, item_text: str):
        if item_text == "Calendar":
            self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "CalendarScreen"
        elif item_text == "Cooking":
            if self.root.ids.main_screen_manager.current == 'CalendarScreen':
                self.root.ids.main_screen_manager.transition.direction = 'left'
            else:
                self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "CookingScreen"
        elif item_text == "3D Print":
            if self.root.ids.main_screen_manager.current == 'CalendarScreen' or self.root.ids.main_screen_manager.current == 'CookingScreen':
                self.root.ids.main_screen_manager.transition.direction = 'left'
            else:
                self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "PrintScreen"
        elif item_text == "Home":
            self.root.ids.main_screen_manager.transition.direction = 'left'
            self.root.ids.main_screen_manager.current = "HomeScreen"

if __name__ == "__main__":
    global lists
    #global calendars
    global mainapp
#    lists = Lists()
    #calendars = Calendars()

    mainapp = HomeDisplayApp()
    mainapp.run()
    sys.exit(0)

    lists.update()
    calendars.update()
