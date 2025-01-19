import keyring
import gkeepapi
import sys

class Notes:
    def __init__(self, user_email):
        # Get google oauth key from keyring
        try:
            self.google_oauth_key = keyring.get_password("google_oauth", user_email)
        except Exception as error:
            print(f"Error getting Google OAuth key from keyring:\n   {error}")
            sys.exit(-1)

        # Connect to Google Keep
        try:
            self.keep = gkeepapi.Keep()
            self.keep.authenticate(user_email, self.google_oauth_key)
        except Exception as error:
            print(f"Error logging into to Google Keep:\n   {error}")
            sys.exit(-1)

    def update(self):
        try:
            self.keep_all = self.keep.all()
            self.keep_notes = [ node for node in self.keep_all if type(node) == gkeepapi.node.Note]
        except Exception as error:
            print(f"Error downloading data:\n   {error}")
            sys.exit(-1)