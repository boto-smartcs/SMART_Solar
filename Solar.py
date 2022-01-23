import serial
import paho.mqtt.client as paho
from time import sleep
from datetime import datetime
import jsonData
import sys,re,os,subprocess
from subprocess import PIPE, Popen
import psutil
import json
import socket
import ipaddrp
import ntplib
import pandas as pd
import schedule
print('Solar > Serial port initialization.')
print('Soalar > Serial port baudrate is 115200bps.')


PORT_NUMBER = '/dev/ttyS0'
BAUDRATE = 115200
MESSAGE_LENGTH = 8
HEADER_NUMBER = float(112)


COM1 = serial.Serial(port = PORT_NUMBER, baudrate = BAUDRATE, parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)




#
################################################################################
#
#	Check Net connection
#

def CheckNetwork():
    s = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except socket.error as msg:
        print(msg)
        s.close()
        s = None

    if s is None:
        return s

    s.close()
    return ip



def ConnectionNetwork():
    print("Solar raspberry pi connection request...")
    #sleep(60)
    while True:
        if CheckNetwork() is None:
            print("No internet connection! ")
            sleep(1)
            os.system('sudo reboot')
        break

    while True:
        if CheckNetwork() is not None:
            print("Device name: " + os.uname()[1])
            print("Solar rpi > Connecting the network " + CheckNetwork())
            ipaddr, gateway, subnetmask = ipaddrp.getNetworkIp()
            print("Gateway: " + gateway)
            print("Subnetmask: " + subnetmask)
            print("UART is open: ", COM1.isOpen())
            break

def ntpTime():
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    t = datetime.fromtimestamp(response.tx_time)
    time_ntp = t.strftime("%m %d %H:%M:%S %Y")  # Mon Jul 05 13:58:39 2021
    print('NTP Time = ' + str(time_ntp))
    # os.system('w32tm /resync')
    os.system('date ' + t.strftime("%x"))
    os.system('time ' + t.strftime("%X"))

def cpuTemp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*', msg)  # a solution with a  regex
        try:
            temp = float(m.group())
        except ValueError:  # catch only error needed
            pass
    return temp, msg

def getCPUuse():
    return str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())

###########################################################################
#
#               Mqtt callback functions
#
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

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

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload,'utf-8'))

    if msg.payload == b"reset!":
        os.system('sudo reboot')

def on_log(mosquitto, obj, level, string):
	print('MQTT > log - ' + string)

def Mqttcallback():
    client = paho.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.connect("180.64.29.99", 1883, 60)
    client.loop_start()
    return client

# send data 1 day one time
def oneDayJob():

    clientMqtt = Mqttcallback()
    now = datetime.now()

    dateTime = now.strftime("%m/%d/%Y:%H_%M_%S")
    ddata = jsonData.Object()
    ddata.Today = dateTime

    info_packet = [0x5a, 0x04, 0x00, 0x00, 0x00, 0x00, 0xa5]
    COM1.write(bytearray(info_packet))

    bytes_data1 = COM1.read(8)
    byteArrData = list(bytes_data1)
    print(bytes_data1)
    print(byteArrData)

    consumeEnergy = float((byteArrData[0] << 8) + byteArrData[1]) / 100


    ddata = jsonData.Object()
    ddata.Today = jsonData.Object()
    ddata.Today.PV = jsonData.Object()
    ddata.Today.PV.Generate = 100
    ddata.Today.PV.Peak = 100

    ddata.Today.PV.Battery = jsonData.Object()
    ddata.Today.PV.Battery.Efficiency = 90

    ddata.Today.PV.Load = jsonData.Object()
    ddata.Today.PV.Load.TotalCurrent = 50
    ddata.Today.PV.Load.TotalCurrent2 = 10

    ddata.Today.PV.Status = jsonData.Object()
    ddata.Today.PV.Status.Estimated_Charge_Time = 2

    clientMqtt.publish("Solar/cmd/D_ID", str(ddata.toJSon()), qos=1)
    print(ddata.toJSon())
    clientMqtt.loop_stop()
    print('mqttc: one day loop_stop')
    clientMqtt.disconnect()


def oneHJob():

    clientMqtt = Mqttcallback()

    now = datetime.now()


    dateFile = now.strftime("%H_%M_%S")
    filename = '/home/pi/SolarPro/files'+'Solar_'
    pd.set_option('display.max_rows', 500)

    with open(filename+dateFile+'.csv', 'a', encoding='utf-8') as wr_file:
        wr_file.write("pv_volt_h, pv_volt_, pv_x_H\n")

    #while (True):
    now = datetime.now()
    info_packet = [0x5a, 0x00, 0x00, 0x00, 0xa5]
    COM1.write(bytearray(info_packet))
    sleep(1)
    counter = COM1.in_waiting
    print(counter)
    if counter > 8:
            bytes_data = COM1.read(20)

            byteList = list(bytes_data)

            #print(bytes_data)
            print(byteList)

            pv_volt_h =  float((byteList[1] << 8) +  byteList[2]) / 100
            pv_current = float((byteList[3] << 8) +  byteList[4]) / 100
            pv_power = float((byteList[5] << 8) +  byteList[6]) / 100
            print("load_power", byteList[14])

            bat_volt_h = float((byteList[7] << 8) + byteList[8]) / 100

            load_volt_current = float((byteList[10] << 8) + byteList[11]) / 100
            load_Current = float((byteList[12] << 8) + byteList[13]) / 100
            load_power = float((byteList[14] << 8) + byteList[15]) / 100

            temp_h = float((byteList[16] << 8) + byteList[17]) / 100

            AvTime = pv_power / load_power

            data = jsonData.Object()
            data.Solar = jsonData.Object()
            data.Solar.D_ID = "Solar1"

            data.Solar.PV = jsonData.Object()
            data.Solar.PV.Volt = pv_volt_h
            data.Solar.PV.Current = pv_current
            data.Solar.PV.Power = pv_power

            data.Solar.Battery = jsonData.Object()
            data.Solar.Battery.Volt = bat_volt_h
            data.Solar.Battery.Current = load_volt_current
            data.Solar.Battery.Remaning = str(byteList[9]) + '%'

            data.Solar.Load = jsonData.Object()
            data.Solar.Load.Volt = load_volt_current
            data.Solar.Load.Current = load_Current
            data.Solar.Load.Power = load_power

            data.Solar.Status = jsonData.Object()
            data.Solar.Status.Controller_Temperature = temp_h
            data.Solar.Status.UPTIME = now.strftime("%Y-%m-%d, %H:%M:%S")
            data.Solar.Status.AvailableTime = AvTime


            print(data.toJSon())

            clientMqtt.publish("Solar/cmd/D_ID", str(data.toJSon()), qos=1)

            datas = pd.DataFrame([[str(byteList[1]),  str(byteList[2]),  str(byteList[3])]])
            with open(filename+dateFile+'.csv', 'a', newline = '\n') as fil:
                datas.to_csv(fil, index= False, header = False)

            sleep(1)
    #datas.close()
    clientMqtt.loop_stop()
    print('mqttc: loop_stop')
    clientMqtt.disconnect()

if __name__ == '__main__':
    ConnectionNetwork()
    #oneHJob()
    #schedule.every().hour.do(oneDayJob)
    schedule.every(2).seconds.do(oneHJob)
    #schedule.every().day.at("10:30").do(job)

    while True:
        schedule.run_pending()
        sleep(1)

