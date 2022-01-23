import paho.mqtt.client as mqtt
from time import sleep

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("ITS/solar/request")
   #client.subscribe("$feeder/topic")

def on_publish(mosquitto, obj, mid):
	print('MQTT > Pub : mid :' + str(mid))

def on_subscribe(mosquitto, obj, mid, granted_qos) :
	print('MQTT > Subscribed: ' + str(mid) + ' ' + str(granted_qos))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload,'utf-8'))

    if msg.payload:
        client.publish("ITS/solar/request", str("Hello form _______________my PC "), qos=1)
        # Do something
    if msg.payload == b"yes!":
        print("Received message #2, do something else")
        # Do something else

if __name__=="__main__":
    # Create an MQTT client and attach our routines to it.
    global client
    client = mqtt.Client()
    client.connect("180.64.29.99", 1883, 60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe

    #client.publish("ITS/solar/request", str("Hello form _______________my PC "), qos=1)
    client.loop_forever()