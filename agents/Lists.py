import gkeepapi
import keyring
import sys
import time
from todoist_api_python.api import TodoistAPI
from globals import user_email, google_oauth_key, todoist_api_key

class Lists:
    def __init__(self, screen_obj):
        # Connect to Google Keep
        try:
            self.keep = gkeepapi.Keep()
            self.keep.authenticate(user_email, google_oauth_key)
        except Exception as error:
            print(f"Error logging into to Google Keep:\n   {error}")
            sys.exit(-1)

        self._screen_obj = screen_obj

        ## Connect to Todoist
        #try:
        #    self.todoist_api = TodoistAPI(todoist_api_key)
        #except Exception as error:
        #    print(f"Error logging into to Todoist:\n   {error}")
        #    sys.exit(-1)

    def update(self):
        #try:
        #    self.todoist_tasks = self.todoist_api.get_tasks()
        #except Exception as error:
        #    print(f"Error loading tasks from Todoist:\n   {error}")
        #    sys.exit(-1)

        done = False
        while not done:
            print("Downloading data from Google Keep...")
            try:
                self.keep.sync()
                self.keep_all = self.keep.all()
    
                # Get all lists into a dictionary
                self.keep_dict = { node.title: node for node in self.keep_all if type(node) == gkeepapi.node.List }
            except Exception as error:
                print(f"Error downloading data:\n   {error}")
                print("Retrying in 10 seconds...")
                time.sleep(10)
                #sys.exit(-1)
            
            done = True
            print("Done")

    def push(self):
        try:
            self.keep.sync()
        except Exception as error:
            print(f"Error syncing with Google Keep:\n   {error}")
            sys.exit(-1)

    def __getitem__(self, key):
        return self.keep_dict[key]
    
    def __setitem__(self, key, value):
        self.keep_dict[key] = value

    def __delitem__(self, key):
        del self.keep_dict[key]

    def __contains__(self, key):
        return key in self.keep_dict
    
    def __iter__(self):
        return iter(self.keep_dict)
    
    def __len__(self):
        return len(self.keep_dict)
    
    def items(self):
        return self.keep_dict.items()
    
    def args_converter(self, row_index, rec):
        return {'text': rec._text, 'size_hint_y': None, 'height': 25}