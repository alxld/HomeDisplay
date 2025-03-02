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

## TODO: Check dates coming from Todoist.  Timezone looks wrong.
## TODO: Pop-up to select which Lists to show
## TODO: Pop-up to select which Calendars to show
## TODO: Figure out why switch_to_hour isn't getting bound and called
## TODO: Add arrows to scroll through months

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'multi')
Config.set('kivy', 'exit_on_escape', 0)

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
import sys
from screens.CalendarScreen import CalendarScreen
from screens.WorkoutScreen import WorkoutScreen
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

    def on_switch_tabs(self, bar: MDNavigationBar, item: MDNavigationItem, item_icon: str, item_text: str):
        new_screen_name = item_text.replace('3D ', '') + "Screen"

        new_idx = self.root.ids.main_screen_manager.screen_names.index(new_screen_name)
        curr_idx = self.root.ids.main_screen_manager.screen_names.index(self.root.ids.main_screen_manager.current)

        if new_idx > curr_idx:
            self.root.ids.main_screen_manager.transition.direction = 'left'
        else:
            self.root.ids.main_screen_manager.transition.direction = 'right'
        
        self.root.ids.main_screen_manager.current = new_screen_name

if __name__ == "__main__":
    mainapp = HomeDisplayApp()
    mainapp.run()
    sys.exit(0)
