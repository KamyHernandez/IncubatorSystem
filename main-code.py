import serial, time, csv, os
import logging
import numpy as np
import heartpy as hp
import smbus2 as smbus
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import platform
import timeit
import cayenne.client
from timeit import default_timer as timer_s
from time import perf_counter
from scipy.signal import peak_widths
from scipy.signal import peak_prominences
from scipy.signal import find_peaks
from scipy.signal import find_peaks_cwt
from scipy.signal import resample
from scipy.fft import fft, ifft
from scipy.signal import butter, lfilter
from smbus2 import SMBus

print("Imported Platform module version: ", platform.__version__)
print("Matplotlib version: "+mpl.__version__)

##I2C SLAVES  SET UP
DHT_ADDRESS = 8 #0x08
OXY_ADDRESS = 11 #0x0b
#slavex_address = xxxx #write address
#slavey_address = xxxx #write address
#slavez_address = xxxx #write address
bus = SMBus(1) #indicates /dev/ic2-1


##CAYENNE SERVICE
# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "4d158210-e641-11eb-8779-7d56e82df461"
MQTT_PASSWORD  = "ca89ad8811a5ea3006523a32946b58491a1a4c65"
MQTT_CLIENT_ID = "b65c60f0-4761-11ec-ad90-75ec5e25c7a4"


client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883)


timestamp = 0


if __name__ == '__main__':
    #Create I2C BUS
    I2Cbus = smbus.SMBus(1)

    with smbus.SMBus(1) as I2Cbus:
        slaveSelect = input("Which device (1-2): ")

        if slaveSelect == "1":
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
            ser.flush()  
            oxy_data=bus.read_byte(OXY_ADDRESS,0)
            timer = []
            hrdata= []
            start_word = False
            while True:
                
                try:
                    data = ser.readline().decode('utf-8').rstrip()
                    #time.sleep(0.3)
                    hrdata.append(data) # append to data vector           
            
                    time_arr = round(time.time())
                    print(type(time_arr))
                    timer.append(time_arr)
                    print(hrdata)
                    if len(hrdata) > 25:
                        break
            
                except KeyboardInterrupt:
            
                    break
            
            print("Exited Loop")   
            hrdata_arr=np.array(hrdata)
            timer_arr=np.array(timer)    
            #Sample Rate
            fs=hp.get_samplerate_mstimer(timer_arr)
            print("fs: ",fs)    
            #String to Int
            for i in range(len(hrdata_arr)):
                hr_int=hrdata_arr.astype(np.int32)
                #hr_int=np.empty_like(hrdata_arr, dtype = int)        
    
            print("PPG data: ",hr_int)

            time.sleep(0.4)
            print("Extracting measurements...")
            time.sleep(1)
            
            #Heart Rate
            hr_fft=np.fft.fft(hr_int)
            print("FFT: ",hr_fft)
            freq=np.fft.fftfreq(len(hr_fft))
            
            print("hr_fft: ",hr_fft)
            fft_peak=find_peaks(hr_fft,threshold=350,distance=30)
            print("Peaks from FFT: ",fft_peak)
    
            bpm=(np.mean(fft_peak[:1])*6)
            
            
            #SBP Calculation
            pks=find_peaks(hr_int,threshold=400, distance=20, width=50,prominence=200)
            add = (sum(pks[:1]))
            div = len(pks[:1])
            p=(np.diff(np.sign(np.diff(hr_int))) < 0).nonzero()[0] + 1 
    
            print("Peaks Detected: ",p)
            sys=np.mean(p)*8
    
            

            #DBP Calculation
            vall=find_peaks(hr_int,threshold=200, distance=20)    
            add2 = sum(vall[:1])
            div2 = len(vall[:1])
            v=(np.diff(np.sign(np.diff(hr_int))) > 0).nonzero()[0] + 1
            print("local min: ",v)
            v_mean = np.mean(v)*8
            print(v_mean)
            dias=(sys-38)*0.9996
            print("Valleys detected: ",vall[:1])

            #MAP Estimation
            m_ap=(dias+(2*dias))*0.33
            print("Heart Rate: ",bpm)
            print("SBP: ",sys)
            print("DBP:", dias)
            print("Mean Arterial Pressure: ",m_ap)

            #Send data to CayenneMQTT
            while True:
    
                client.loop()
                if (time.time() > timestamp + 10):
                    client.virtualWrite(1,bpm)
                    client.virtualWrite(3,sys)
                    client.virtualWrite(4,dias)
                    timestamp = time.time()
        
                    time.sleep(0.3)
                    
        if slaveSelect == "2":
            #opening serial port
            ser=serial.Serial('/dev/ttyACM0', 9600)            
            temp = []
            while True:
                tem=bus.read_byte_data(OXY_ADDRESS,0)
                print("data from DHT22: ", tem)
                print(type(tem))
                serialdata=ser.readline().decode('utf-8').rstrip() 
                print("data recieved: ",serialdata)
                temp.append(serialdata)
                print(type(temp))
                print("temp: ",temp)
                #temp=int(serialdata)
                client.loop()
                client.virtualWrite(2,temp)
                time.sleep(0.3)

        #WRITE ADDRESS OF ADITIONAL SENSORS
        
        #if slaveSelect == "3":
        #   while True:
        #        data1=bus.read_byte_data(slavex_address,0)
        #        client.loop()
        #        chan_x=5
        #        client.virtualWrite(chan_x,data1)
        #        time.sleep(0.3)
        #if slaveSelect == "4":
        #    while True:
        #        data2=bus.read_byte_data(slavex_address,0)
        #        client.loop()
        #        chan_y=6
        #        client.virtualWrite(chan_y,data2)
        #        time.sleep(0.3)
        
        #if slaveSelect == "5":
        #    while True:
        #        data3=bus.read_byte_data(slavex_address,0)
        #        client.loop()
        #        chan_z=7
        #        client.virtualWrite(chan_z,data3)
        #        time.sleep(0.3)
            

