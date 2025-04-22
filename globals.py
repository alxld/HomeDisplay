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

# Workout MySQL
workout_host = "192.168.1.7"
workout_user = "adeno"
workout_password = keyring.get_password("mysql", "adeno")

# Home Assistant
HA_URL = "http://homeassistant.local:8123"
#HA_TOKEN = keyring.get_password("homeassistant", "token")
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxNDQ1ZDEzYjQ4ZWY0NWNiYjU4NDM5MGE2NzE2YjEwMyIsImlhdCI6MTc0NDU2NDAxMiwiZXhwIjoyMDU5OTI0MDEyfQ.5c9GYxEhw4RSsDKZj5Mife5jjIqNGhMBxefVJW9mh5k"
#HA_CALENDAR_IDS = ['calendar.aarondeno11_gmail_com', 'calendar.birthdays', 'calendar.christian_holidays']
HA_CALENDAR_URL = f"{HA_URL}/api/calendars"
HA_HEADER = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json"
}
HA_CALENDAR_COLORS = {
    'calendar.aarondeno11_gmail_com': [167/255, 90/255, 186/255],
    #'calendar.christian_holidays': [66, 154, 142],
    #'calendar.hex_calendar': [132, 140, 194],
    'calendar.holidays_in_united_states': [66/255, 154/255, 142/255],
    #'calendar.logan_s_calendar': [102, 139, 225],
    #'calendar.louise_s_calendar': [167, 90, 186],
    #'calendar.phases_of_the_moon': [174, 156, 206],
    #'calendar.pura': [153, 188, 245]

}