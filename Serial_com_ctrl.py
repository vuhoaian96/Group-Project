import serial.tools.list_ports
import time
import matplotlib.pyplot as plt 
import csv
from drawnow import drawnow, figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import numpy as np


class SerialCtrl():
    def __init__(self):
        self.com_list = []
        self.connect_list = []
        self.foundports = []
        self.sync_cnt = 200
        self.force_distance = 0
        self.motor_data = ""

    def getCOMList(self):
        ports = serial.tools.list_ports.comports()
        return ports

    def findArduino(self):

        self.foundports = self.getCOMList()
        numConnection = len(self.foundports)
        self.commPorts = str()

        for i in range(0,numConnection):
            port = self.foundports[i]
            strPort = str(port)
            
            # if 'Arduino' in strPort:
            splitPort = strPort.split(' ')
            self.commPorts = splitPort[0]

        return self.commPorts
    
    
    def SerialOpen(self,gui):
        try:
            self.ser.is_open
        except:
            PORT = gui.clicked_com.get()
            BAUD = gui.clicked_bd.get()
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
        
        try:
            if self.ser.is_open:
                self.ser.status = True
            else:
                PORT = gui.clicked_com.get()
                BAUD = gui.clicked_bd.get()
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.open()
                self.ser.status = True

        except:
            self.ser.status = False
    def SerialClose(self):
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
        except: 
            self.ser.status = False

    def send_to_motor(self, field):
        if self.ser.is_open:
            print("sending to motor")
            data = ','.join(map(str, field))
            print(data)     #----------> data sẽ có định dạng như sau: "1,2,3"
            # gửi data cho arduino
            self.ser.write(data.encode())
        else:
            print("Serial port not open")

    def read_serial(self,gui):
        self.threading = True
        self.ser.write(b's')
        while self.threading:
            try:
        # Read a line from the serial port
                
                gui.received_data = self.ser.readline().decode("utf-8").strip('\r\n')
                
                if gui.received_data:
                    data = gui.received_data.split(',')
                    a = data[0]
                    b = data[1]
                    c = data[2]
                    gui.distance.append(b) #add incoming distance data into array
                    gui.force.append(a)
                    gui.time.append(c)
                    print(f"Force: {a}, Distance: {b}, Time: {c}")
                    gui.animate(gui.distance, gui.force, gui.time)

                
                if self.threading == False:
                    break
            except Exception as e:
                print(f"Error reading serial data: {e}")      


    def stop_read(self):
        self.threading = False

    def playback(self):
        self.threading = True
    
    def sending_stop(self):
        self.ser.write(b'e')
        self.threading = False


if __name__ == "__main__":
    SerialCtrl()