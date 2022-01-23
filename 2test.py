import serial
import paho.mqtt.client as mqtt
from time import sleep
import time
import binascii
import sys,re
import struct
import jsonData
from datetime import datetime
import codecs
import bitstring

now = datetime.now()

print('Solar > Serial port initialization.')
print('Soalar > Serial port baudrate is 115200bps.')


PORT_NUMBER = '/dev/ttyS0'
BAUDRATE = 115200
MESSAGE_LENGTH = 8
HEADER_NUMBER = float(112)


COM1 = serial.Serial(port = PORT_NUMBER, baudrate = BAUDRATE, parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)


print("UART is open: ", COM1.isOpen())

thresting  = "7E FF 03 00 01 00 02 0A 01 C8 04 D0 01 02 80 00 00 00 00 8E E7 7E"


#
################################################################################
#
#	Transmit Serial Data
#
def SerialTransmit(data_type, data1, data2) :
	tx_buffer = [ '$', 0, 0, 0, 0, '\r' ]

	tx_buffer[1] = data_type	# 'S'
	tx_buffer[2] = data1
	tx_buffer[3] = data2
	tx_buffer[4] = int(tx_buffer[1]) ^ int(tx_buffer[2]) ^ int(tx_buffer[3])

	COM1.write(bytearray(tx_buffer[0:6]))

def SerTrsnamit(data, data2, data3, data4):
    tx_buffer = ['$', 0, 0, 0, 0, 0, '\r']
    tx_buffer[1] = data  # 'S'
    tx_buffer[2] = data2
    tx_buffer[3] = data3
    tx_buffer[4] = data4
    tx_buffer[5] = int(tx_buffer[1]) ^ int(tx_buffer[2]) ^  int(tx_buffer[3]) ^ int(tx_buffer[4])
    #tx_buffer[5] = int
    #print(bytearray(tx_buffer[1:6]))

    COM1.write(bytearray(tx_buffer[1:6]))


def get_version():
    ##########################
    # get version info
    info_packet = [0x5a, 0x04, 0x14, 0x00]

    COM1.write(info_packet)
    time.sleep(0.1)
    bytes_to_read = 30
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = COM1.in_waiting
        if counter > bytes_to_read:
            bytes_data = COM1.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                version = bytes_data[3:-1].decode('utf-8')
                print('Version -' + version)
                return
            else:
                COM1.write(info_packet)
                time.sleep(0.1)
def bitwise_xor_bytes(a, b):
    result_int = int.from_bytes(a, byteorder="big") ^ int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")

def readData():
    rx_buffer = [0, 0, 0, 0, 0, 0]
    #data = struct.pack(hex(thresting))
    while (True):
        #info_packet = [0x5a, 0x00, 0x00, 0x00, 0xa5]
        #info_packet = [0x04, 0x00, 0x00, 0x00, 0xa5]

        info_packet = [0x5a, 0x04, 0x00, 0x00, 0xa5]
        COM1.write(bytearray(info_packet))
        bytes_data1 = COM1.read(8)
        byteArrData = list(bytes_data1)
        print(bytes_data1)
        print(byteArrData)
        #COM1.write(info_packet)
        time.sleep(1)



if __name__ == '__main__':
        readData()

