import pandas as pd
import datetime
import time
from statistics import mean
from tkinter import IntVar

def folderData(avg, peak):
    named_tuple = time.localtime()  # get struct_time
    time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
    filedate = time.strftime("%Y-%m-%d", named_tuple)

    txtfilename = "C:/Users/User/Desktop/SolarPro/" + filedate + ".csv"

    datas = pd.DataFrame([[0, avg, peak, time_string]])

    print(time_string)
    with open(txtfilename, 'a', newline='\n') as fil:
        datas.to_csv(fil, index=False, header=False)
        print("done")
    fil.close()

def rfolderData():

    dago = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')  # get one day ago file name
    # dAgo = time.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), "%Y-%m-%d")
    try:
        listAvg = []
        list1Max = []
        #Solardate = pd.read_csv("C:/Users/User/Desktop/SolarPro/" + dago + ".csv")
        Solardate = pd.read_csv("C:/Users/User/Desktop/SolarPro/2021-12-24.csv", names=['avgVal', 'maxVal', 'date'])
        avgVal = "{:.2f}".format(Solardate['avgVal'].mean())
        peakVal = Solardate['maxVal'].max()

        print(avgVal, peakVal)
        #return avgVal, peakVal
    except FileNotFoundError:
        print('\n\tSorry, \'', FileNotFoundError.__filename__, '\' not found.\n')
        return 0, 0

def batVal(batval):
    #txtfilename = "/home/pi/Solar/files/batVal.csv"
    txtfilename = "C:/Users/User/Desktop/SolarPro/batVal.csv"
    datas = pd.DataFrame([[batval]])
    with open(txtfilename, 'w', newline='\n') as fil:
        datas.to_csv(fil, index=False, header=False)
    fil.close()
    print("done.....")

def rbatval():
    try:
        SolarBatVal = "C:/Users/User/Desktop/SolarPro/batVal.csv"
        with open(SolarBatVal) as f:
            values = f.read()
        return int(values)
    except FileNotFoundError:
        print('\n\tSorry, \'', FileNotFoundError.__filename__, '\' not found.\n')
        return 0

if __name__ == '__main__':
    folderData(6,5)
    rfolderData()
    #avgVal, peakVal = rfolderData()
    #print(avgVal,"   ", peakVal)