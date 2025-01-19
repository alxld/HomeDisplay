import gkeepapi
import keyring
import sys
from todoist_api_python.api import TodoistAPI

class Lists:
    def __init__(self, user_email):
        # Get google oauth key from keyring
        try:
            self.google_oauth_key = keyring.get_password("google_oauth", user_email)
        except Exception as error:
            print(f"Error getting Google OAuth key from keyring:\n   {error}")
            sys.exit(-1)

        # Get todoist api key from keyring
        try:
            self.todoist_api_key = keyring.get_password("todoist_api", user_email)
        except Exception as error:
            print(f"Error getting Todoist API key from keyring:\n   {error}")
            sys.exit(-1)

        # Connect to Google Keep
        try:
            self.keep = gkeepapi.Keep()
            self.keep.authenticate(user_email, self.google_oauth_key)
        except Exception as error:
            print(f"Error logging into to Google Keep:\n   {error}")
            sys.exit(-1)

        # Connect to Todoist
        try:
            self.todoist_api = TodoistAPI(self.todoist_api_key)
        except Exception as error:
            print(f"Error logging into to Todoist:\n   {error}")
            sys.exit(-1)

    def update(self):
        try:
            self.todoist_tasks = self.todoist_api.get_tasks()
        except Exception as error:
            print(f"Error loading tasks from Todoist:\n   {error}")
            sys.exit(-1)

        try:
            self.keep_all = self.keep.all()
            self.keep_lists = [ node for node in self.keep_all if type(node) == gkeepapi.node.List ]
        except Exception as error:
            print(f"Error downloading data:\n   {error}")
            sys.exit(-1)