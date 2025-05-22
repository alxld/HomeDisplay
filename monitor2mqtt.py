import paho.mqtt.client as mqtt
from monitorcontrol import monitorcontrol
from globals import mqtt_name, mosquitto_ip, mosquitto_username, mosquitto_password
import sys

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(f"{mqtt_name}/monitor/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == f"{mqtt_name}/monitor/monitor_on":
        monitor_on()
    elif msg.topic == f"{mqtt_name}/monitor/monitor_dim":
        monitor_dim()
    elif msg.topic == f"{mqtt_name}/monitor/monitor_very_dim":
        monitor_very_dim()
    elif msg.topic == f"{mqtt_name}/monitor/monitor_off":
        monitor_off()

try:
    monitors = monitorcontrol.get_monitors()
    print(monitors)
except Exception as error:
    print(f"Error getting monitors:\n   {error}")
    sys.exit(-1)
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def monitor_on():
    for monitor in monitors:
        with monitor:
            monitor.set_power_mode(1)
            monitor.set_luminance(100)
            monitor.set_contrast(70)

def monitor_off():
    for monitor in monitors:
        with monitor:
            monitor.set_power_mode(4)

def monitor_dim():
    for monitor in monitors:
        with monitor:
            monitor.set_power_mode(1)
            monitor.set_luminance(50)
            monitor.set_contrast(0)

def monitor_very_dim():
    for monitor in monitors:
        with monitor:
            monitor.set_power_mode(1)
            monitor.set_luminance(25)
            monitor.set_contrast(0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.username_pw_set(mosquitto_username, mosquitto_password)
client.connect(mosquitto_ip, 1883, 60)

client.loop_forever()
