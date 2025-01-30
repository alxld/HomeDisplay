import keyring
import sys
import socket

user_email = "aarondeno11@gmail.com"

try:
    google_oauth_key = keyring.get_password("google_oauth", user_email)
except Exception as error:
    print(f"Error getting Google OAuth key from keyring:\n   {error}")
    sys.exit(-1)

try:
    todoist_api_key = keyring.get_password("todoist_api", user_email)
except Exception as error:
    print(f"Error getting Todoist API key from keyring:\n   {error}")
    sys.exit(-1)

# Fullscreen on my release machines
if socket.gethostname() == "sabertooth":
    fullscreen = False
else:
    fullscreen = True

# MQTT naming
mqtt_base = "alxld"
mqtt_mid = "HomeDisplay"
mqtt_suffix = "Kitchen"
mqtt_name = f"{mqtt_base}/{mqtt_mid}/{mqtt_suffix}"
mosquitto_ip = "192.168.1.7"
mosquitto_username = "hass"
mosquitto_password = keyring.get_password("mosquitto", "hass")