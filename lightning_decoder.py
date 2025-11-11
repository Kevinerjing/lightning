import io
import time
import json
import subprocess
import paho.mqtt.client as mqtt

broker = "866f25366b704f7082cf5f69e15eea34.s1.eu.hivemq.cloud"
port = 8883
username = "lightningalert"
password = "IDontknow123!"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)

def on_publish(client, userdata, mid):
    print("Message published with mid:", mid)

client = mqtt.Client()
client.username_pw_set(username, password)
client.tls_set()
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(broker, port, 60)
client.loop_start()

#--- Real device: rtl_433 output ---

proc_stdout = subprocess.Popen(
    ["rtl_433", "-F", "json"],
    stdout=subprocess.PIPE,
    text=True
).stdout


last_strike_count = None

for line in proc_stdout:
    try:
        data = json.loads(line.strip())
        model = data.get("model")

        # Only publish if strike_count is different from last one
        strike_count = data.get("strike_count")
        if model == "Acurite-6045M" and strike_count != last_strike_count:
            print("Publishing new strike:", data)
            client.publish("kanata/lightning-station-001", json.dumps(data), qos=1, retain=True)
            last_strike_count = strike_count

    except Exception as e:
        print("Parse error:", e)

