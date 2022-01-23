import paho.mqtt.client as paho
import time

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

if __name__ == '__main__':

    client = paho.Client()
    client.on_publish = on_publish
    #client.connect("broker.mqttdashboard.com",1883,60)
    client.connect("180.64.29.99", 1883, 60)
    client.loop_start()

    while True:
        messege = "nice"
        (rc, mid) = client.publish("ITS/solar/status", str(messege), qos=1)
        time.sleep(1)