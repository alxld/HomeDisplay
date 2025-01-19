# pip install todoist-api-python google-api-python-client google-auth-httplib2 google-auth-oauthlib

# If Google Calendar stops authenticating, go here:
#   https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html#getting-started
# and download the .json file to ~/.credentials and delete token.pickle.

# To get gkeepapi master token, go here:
#   https://accounts.google.com/EmbeddedSetup
# Open the debug console with F-12.  Go through all the prompts.  Once you click 'I agree', QUICKLY
# copy and paste the oauth_token field and paste it into README/token_exchange.py.  Run the script in
# the debugger (not sure why it won't print right) and grab the value of master_response['Token'].
# Save that into keyring's google_oauth.

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
import sys
from screens.CalendarScreen import CalendarScreen
from screens.CookingScreen import CookingScreen
from screens.HomeScreen import HomeScreen
from screens.PrintScreen import PrintScreen
from globals import fullscreen

class HomeDisplayApp(MDApp):
    def on_start(self):
        #self.fps_monitor_start()
        super(HomeDisplayApp, self).on_start()

    def build(self):
        Window.size=(1920, 1080)
        Window.fullscreen = fullscreen
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
