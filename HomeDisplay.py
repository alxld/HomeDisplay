# pip install todoist-api-python google-api-python-client google-auth-httplib2 google-auth-oauthlib

# If Google Calendar stops authenticating, go here:
#   https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html#getting-started
# and download the .json file to ~/.credentials and delete token.pickle.

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
import sys
import keyring
from screens.CalendarScreen import CalendarScreen
from screens.CookingScreen import CookingScreen
from screens.HomeScreen import HomeScreen
from screens.PrintScreen import PrintScreen

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
    mainapp = HomeDisplayApp()
    mainapp.run()
    sys.exit(0)

    #lists.update()
    #calendars.update()
