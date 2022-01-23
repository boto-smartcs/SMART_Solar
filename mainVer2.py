import datetime
import time
import serial
import socket
import paho.mqtt.client as mqtt
import json
from Object import Object
import schedule
import requests
import os
import filesman

# configure the serial connections (the parameters differs on the device you are connecting to)
print('Solar > Serial port initialization.')
print('Solar > Serial port baudrate is 115200bps.')

COM1 = serial.Serial(
    port='/dev/ttyS0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

IP = '180.64.29.99'
Topic = '/Solar/state/Solar1'
Sub = '/Solar/cmd/Solar1'


cmd = [0x5a, 0x00, 0x00, 0x00, 0xa5]
tx_buffer = [0x5a, 0x04, 0x00, 0x00, 0x00, 0xa5]
reset_buffer = [0x5a, 0x02, 0x03, 0x00, 0x00, 0xa5]

#
################################################################################
#
#	Check Network connection
#
def CheckNet():
    s = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except socket.error as msg:
        s.close()
        s = None

    if s is None:
        return s
    s.close()
    return ip

def conn_to_net(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

def ConnectionWlan():
    print('Solar > Update wpa connection.')
    print('Solar > Net connection is: ', conn_to_net())
    if conn_to_net() == False:
        print('Solar > Not connection...')
        time.sleep(60)
        os.system("sudo reboot")

    while 1:
        if CheckNet() is not None:
            print('Solar > My IP is ' + CheckNet())
            break

#
################################################################################
#
#	Mqtt Functions
#

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
        print("Connected with result code " + str(rc))
    else:
        print("Bad connection Returned code=", rc)
    client.subscribe(Sub)


def on_disconnect(client, userdata, flags, rc=0):
    print("disconnect :", str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    global SolarSubMass
    SolarSubMass = str(msg.payload, 'utf-8')
    print(msg.topic + " " + str(msg.payload, 'utf-8'))
    if SolarSubMass == 'RESET,0x3ff':
        print("reset...")
        COM1.write(reset_buffer)
        print("reset has been finished!")
        schedule.CancelJob
        time.sleep(2)
        os.system("sudo reboot")

    if SolarSubMass.partition(",")[0] == "Battery":
        print("saved val: ", int(SolarSubMass.split(",",1)[1]))
        filesman.batVal(int(SolarSubMass.split(",",1)[1]))

def tconvert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

#
################################################################################
#
#	one hour sent data function
#

def oneHourWork():

    #cmd = bytearray([0x5a, 0x00, 0x00, 0x00, 0xa5])
    #cmd = [0x5a, 0x00, 0x00, 0x00, 0xa5]
    #tx_buffer = [0x5a, 0x00, 0x02, 0x03, 0xa5]

    while True:
        try:
            named_tuple = time.localtime()  # get struct_time
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
            COM1.write(cmd)

            # print(COM1.read(20))
            byteList = list(COM1.read(20))
            print(byteList)

            pv_volt_h = byteList[1]
            pv_volt_I = byteList[2]
            pv_c_h = byteList[3]
            pv_c_I = byteList[4]
            pv_pw_h = byteList[5]
            pv_pw_I = byteList[6]

            bat_volt_h = byteList[7]
            bat_volt_I = byteList[8]
            bat_soc_remaining = byteList[9]  # Battery SOC(the precentage of battery's remaining capacity)
            filesman.remAmount(byteList[9])

            load_volt_h = byteList[10]
            load_volt_I = byteList[11]
            load_cur_H = byteList[12]
            load_cur_L = byteList[13]
            load_pw_H = byteList[14]
            load_pw_L = byteList[15]

            temp_h = byteList[16]
            temp_I = byteList[17]

            VOLT = float((pv_volt_h << 8) + pv_volt_I) / 100
            CURRENT = float((pv_c_h << 8) + pv_c_I) / 100
            POWER = float((pv_pw_h << 8) + pv_pw_I) / 100

            BATVOLT = float((bat_volt_h << 8) + bat_volt_I) / 100

            LOAD_V = float((load_volt_h << 8) + load_volt_I) / 100
            LOAD_C = float((load_cur_H << 8) + load_cur_L) / 100
            LOAD_PW = float((load_pw_H << 8) + load_pw_L) / 100

            TEMP = float((temp_h << 8) + temp_I) / 100

            #print("_______________________________>>>>>>>", (bat_soc_remaining / LOAD_PW))
            # AvailableTime = ((pv_volt_h << 8) / (pv_pw_h << 8))
            try:
                AvailableTime = "{:.2f}".format(float(bat_soc_remaining / LOAD_PW))
            except ZeroDivisionError:
                AvailableTime = 0

            filesman.folderData(LOAD_V , POWER)

            dt = Object()
            dt.Solar = Object()
            dt.Solar.D_ID = "Solar1"
            dt.Solar.PV = Object()
            dt.Solar.PV.Volt = VOLT
            dt.Solar.PV.Current = CURRENT
            dt.Solar.PV.Power = POWER

            dt.Solar.Battery = Object()
            dt.Solar.Battery.Volt = BATVOLT
            dt.Solar.Battery.Current = CURRENT
            dt.Solar.Battery.Remaining = bat_soc_remaining

            dt.Solar.Load = Object()
            dt.Solar.Load.Volt = LOAD_V
            dt.Solar.Load.Current = LOAD_C
            dt.Solar.Load.Power = LOAD_PW

            dt.Solar.Status = Object()
            dt.Solar.Status.Controller_Temperature = TEMP
            dt.Solar.Status.UPTIME = time_string
            dt.Solar.Status.Available_Time = AvailableTime

            print(dt.toJSON())
            solarMqtt.publish(Topic, dt.toJSON(), qos=1)
            break
        except:
            print("list of one hour is 0")
            pass
    print("one hour mqtt close")
    #client.loop_stop()


# client.subscribe("test", 1)
# client.loop_forever()

#
################################################################################
#
#	one day sent data function
#

def oneDayWork():
    #cmd = [0x5a, 0x00, 0x00, 0x00, 0xa5]
    #tx_buffer = [0x5a, 0x04, 0x00, 0x00, 0x00, 0xa5]
    #reset_buffer = [0x5a, 0x02, 0x03, 0x00, 0x00, 0xa5]

    try:
        COM1.write(cmd)
        byteList = list(COM1.read(20))
        batCapacity = float((byteList[3] << 8) + byteList[4]) / 100
        voltage = float((byteList[7] << 8) + byteList[8]) / 100

        #totalBatCap = float((byteList[10] << 8) + byteList[11]) / 100 # recheck doubt

        remAmount = byteList[9]
    except:
        print("list dats is 0")
        pass

    while True:
        try:
            lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours=0)

            COM1.write(tx_buffer)

            byteArray2 = COM1.read(7)
            byteList2 = list(byteArray2)

            conEngtoday = float((byteList2[1] << 8) + byteList2[2]) / 100
            genEngtoday = float((byteList2[3] << 8) + byteList2[4]) / 100
            batteryAhSub = filesman.rbatval()

            remeiningAmountWh = (remAmount / 100) * (batteryAhSub * voltage)

            AvailableTime = (remAmount / conEngtoday)



            try:
                #bat_eff = ("{:.1f}".format(float((((lastHourDateTime.hour / 100) * batCapacity) * voltage) / genEngtoday - conEngtoday * 100)))
                bat_eff = (((((filesman.rremAmount() - remAmount) / 100) * batteryAhSub) * voltage) / (genEngtoday - conEngtoday)) * 100
            except ZeroDivisionError:
                bat_eff = 0

            try:
                estimatedChangeTime = tconvert(float(((batteryAhSub * voltage) - remAmount) / genEngtoday - conEngtoday))

            except ZeroDivisionError:
                estimatedChangeTime = 0

            #print("estimatedChangeTime", estimatedChangeTime)
            #print(byteList2)
            try:
                avgVal, peakVal = filesman.rfolderData()
                print("avgVa-------l", avgVal)
                print("peakVal-------l", peakVal)
            except:
                avgVal = 0
                peakVal = 0

            dtone = Object()
            dtone.Today = Object()
            dtone.Today.D_ID = "Solar1"
            dtone.Today.PV = Object()
            dtone.Today.PV.Generate = genEngtoday
            dtone.Today.PV.Peak = peakVal

            dtone.Today.Battery = Object()
            dtone.Today.Battery.Efficiency = bat_eff

            dtone.Today.Load = Object()
            dtone.Today.Load.TotalCurrent = conEngtoday

            dtone.Today.Load.Average = float(avgVal)

            dtone.Today.Status = Object()
            dtone.Today.Status.Estimated_Charge_Time = estimatedChangeTime

            print(dtone.toJSON())
            solarMqtt.publish(Topic, dtone.toJSON(), qos=1)

            break
        except:
            print("data is zero")
            pass

        #time.sleep(2)
    print("one day mqtt close")



if __name__ == '__main__':

    ConnectionWlan()
    if COM1.is_open:
        print("port is open")

    global solarMqtt
    solarMqtt = mqtt.Client()
    solarMqtt.on_connect = on_connect
    solarMqtt.on_disconnect = on_disconnect
    solarMqtt.on_subscribe = on_subscribe
    solarMqtt.on_message = on_message
    solarMqtt.connect(IP, 1883)
    solarMqtt.loop_start()

    schedule.every(3).seconds.do(oneHourWork)
    schedule.every(4).seconds.do(oneDayWork)

    #schedule.every(2).minutes.do(oneHourWork)
    #schedule.every(3.3).minutes.do(oneDayWork)
    #schedule.every().hour.do(job)
    #schedule.every().day.at("10:30").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

