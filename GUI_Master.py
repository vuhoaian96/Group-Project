from tkinter import *
from Serial_com_ctrl import SerialCtrl
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from drawnow import drawnow, figure

global frame_exist
frame_exist = False

class RootGUI():
    def __init__(self):
        '''Initializing the root GUI and other comps of the program'''
        self.root = Tk()
        self.root.title("Tensile Tester")
        self.root.geometry("360x120")
        self.root.config(bg="white")


# Class to setup and create the communication manager with MCU
class ComGui():
    def __init__(self, root, serial):
        '''
        Initialize the connexion GUI and initialize the main widgets 
        '''
        # Initializing the Widgets
        self.root = root
        self.serial = serial
        self.frame = LabelFrame(root, text="Com Manager", padx=5, pady=5, bg="white")
        self.label_com = Label(self.frame, text="Available Port(s): ", bg="white", width=15, anchor="w")
        self.label_bd = Label(self.frame, text="Baude Rate: ", bg="white", width=15, anchor="w")

        # Setup the Drop option menu
        self.baudOptionMenu()
        self.ComOptionMenu()

        # Add the control buttons for refreshing the COMs & Connect
        self.btn_refresh = Button(self.frame, text="Refresh", width=10,  command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect", width=10, state="disabled",  command=self.serial_connect)

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 5

        # Put on the grid all the elements
        self.publish()

    def publish(self):
        '''
         Method to display all the Widget of the main frame
        '''
        self.frame.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.label_bd.grid(column=1, row=3)

        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        self.btn_refresh.grid(column=3, row=2)
        self.btn_connect.grid(column=3, row=3)

    def ComOptionMenu(self):
        
        # Generate the list of available coms

        self.serial.findArduino()
        
        self.clicked_com = StringVar()
        self.clicked_com.set("-")
        self.drop_com = OptionMenu(self.frame, self.clicked_com, self.serial.commPorts, command=self.connect_ctrl)

        self.drop_com.config(width=10)

    def baudOptionMenu(self):
        '''
         Method to list all the baud rates in a drop menu
        '''
        self.clicked_bd = StringVar()
        bds = ["-",
               "300",
               "600",
               "1200",
               "2400",
               "4800",
               "9600",
               "14400",
               "19200",
               "28800",
               "38400",
               "56000",
               "57600",
               "115200",
               "128000",
               "256000"]
        self.clicked_bd .set(bds[0])
        self.drop_baud = OptionMenu(self.frame, self.clicked_bd, *bds, command=self.connect_ctrl)
        self.drop_baud.config(width=10)

    def connect_ctrl(self, widget):
        '''
        Mehtod to keep the connect button disabled if all the 
        conditions are not cleared
        '''
        print("Connect ctrl")
        if "-" in self.clicked_com.get() or " " in self.clicked_com.get() or "-" in self.clicked_bd.get():
            self.btn_connect["state"] = "disable"
        else:
            self.btn_connect["state"] = "active"

    def com_refresh(self):
        self.drop_com.destroy()
        self.ComOptionMenu()
        self.drop_com.grid(column=2, row=2, padx=self.padx)
        logic = []
        self.connect_ctrl(logic) 

    def serial_connect(self):
        
        if self.btn_connect["text"] in "Connect":
            self.serial.SerialOpen(self)
            if self.serial.ser.status:
               self.btn_connect["text"] = "Disconnect"
               self.btn_refresh["state"] ="disable"
               self.drop_baud["state"] = "disable"
               self.drop_com["state"] = "disable"
               InfoMSg= f"Succesful to establish connection using {self.clicked_com.get()}"
               messagebox.showinfo("showinfo", InfoMSg)
              
               # display the chanel manager
               self.conn = ConnGUI(self.root, self.serial)
            
            else:
               ErrorMsg = f"Failure to establish connection using {self.clicked_com.get()}"
               messagebox.showerror("showerror", ErrorMsg)
               
        else:
            global frame_exist
            frame_exist = False
            self.serial.sending_stop()
            #self.conn.serial_thread.join()
            self.conn.ConnGUIClose()
            #closing the connection
            self.serial.SerialClose()
            InfoMSg= f"Connection using {self.clicked_com.get()} is now closed"
            messagebox.showinfo("showinfo", InfoMSg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] ="active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"
            self.time = []
            self.force = []
            self.distance = []
            
    
class ConnGUI(ComGui):
    def __init__(self,root,serial):
        self.root = root
        self.serial= serial
        self.force = []
        self.distance = []
        self.time = []
    
        self.received_data = ""
        
        self.speed_value = StringVar()
        self.loop_value = StringVar()
        self.distance_value = StringVar()
        
        self.frame = LabelFrame(root, text="Input Manager", padx= 5, pady = 5, bg='white',width = 80)
        
        #synchronization
        self.ConnManager = Label(self.frame, text="Connection Manager", bg = "white", width = 20, anchor="w")
        
        #stepper motor input
        self.motor_label = Label(self.frame, text ="Motor Input", bg ="white", width = 20, anchor="w")
        self.motor_speed = Label(self.frame, text="Motor speed:", bg = "white", width = 15, anchor="w")
        self.motor_speed_entry = Entry(self.frame, text = "", bg = "white", width =15) #, textvariable=self.serial.speed
        self.motor_distance = Label(self.frame, text= "Distance:",bg = "white", width = 15, anchor="w")
        self.motor_distance_entry = Entry(self.frame, text = "", bg = "white", width =15) #, textvariable=self.serial.distance
        self.motor_loop = Label(self.frame, bg = "white", text = "Loop number:", width = 15, anchor="w")
        self.motor_loop_entry = Entry(self.frame, text = "", bg = "white", width =15, textvariable= self.distance_value)
        self.send_to_motor = Button(self.frame, text="Send", state = "active", width=5, command=self.send_to_motor)
        
        #chart management
        self.Graph_managment = Label(self.frame, text ="Graph Management", bg ="white", width = 20, anchor="w")
        self.force_distance = IntVar()
        self.force_time = IntVar()
        self.distance_time = IntVar()
        self.FD_check = Checkbutton(self.frame, text="Force vs Distance", variable = self.force_distance, onvalue =1, offvalue =0, bg="white", state = "active")
        self.FT_check = Checkbutton(self.frame, text="Force vs Time", variable = self.force_time, onvalue =1, offvalue =0, bg="white", state = "active") #command=self.start_stream)
        self.DT_check = Checkbutton(self.frame, text="Distance vs Time", variable = self.distance_time, onvalue =1, offvalue =0, bg="white", state = "active") #command=self.start_stream)

        #streaming
        self.streaming = Label(self.frame, text ="Streaming", bg ="white", width = 20, anchor="w")
        self.btn_start_stream = Button(self.frame, text="Start", state="active", width=5, command=self.start_stream)
        self.btn_pause_stream = Button(self.frame, text="Pause", state="active", width=5, command=self.toggle_stream)

        #save option
        self.save = False
        self.save_check = Button(self.frame, text="Save data", bg="white", state = "active", command=self.save_data)

        self.separator = ttk.Separator(self.frame, orient = 'vertical')
        self.pady = 5
        self.padx = 20


        self.ConnGUIOpen()

    def send_to_motor(self):
        field = [self.motor_speed_entry.get(), self.motor_distance_entry.get(), self.motor_loop_entry.get()]
        self.serial.send_to_motor(field)
    

    def ConnGUIOpen(self):
        self.root.geometry('1100x250')
        self.frame.grid(row=0,column=4, rowspan=20, columnspan=30, padx=5, pady=5)
        
        self.motor_label.grid(column=1, row=1, pady=self.pady)
        self.motor_speed.grid(column=1, row=2)
        self.motor_speed_entry.grid(column =2, row =2, pady=self.pady)
        self.motor_distance.grid(column=1, row = 3, pady = self.pady)
        self.motor_distance_entry.grid(column=2, row = 3)
        self.motor_loop.grid(column=1, row=4, pady = self.pady)
        self.motor_loop_entry.grid(column=2, row=4)
        self.send_to_motor.grid(column=2, row=5, pady = self.pady)

        self.ConnManager.grid(column=3, row=1, padx=self.padx, pady=self.pady)

        self.Graph_managment.grid(column=3, row = 2, padx=self.padx, pady = self.pady)
        self.FD_check.grid(column=3,row = 3, padx = self.padx, pady = self.pady)
        self.FT_check.grid(column=4, row = 3)
        self.DT_check.grid(column=5, row = 3, padx = self.padx)

        self.streaming.grid(column= 3, row =4, padx=self.padx, pady = self.pady)
        self.btn_start_stream.grid(column=3, row =5, padx=self.padx, pady = self.pady)
        self.btn_pause_stream.grid(column = 4, row =5)

        self.save_check.grid(column=5, row = 5, padx = 30, pady = self.pady)
        self.separator.place(relx = 0.36, rely = 0, relwidth=0.001, relheight=1)


    def ConnGUIClose(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("360x120")

    def EntryMotro(self):
        if "" in self.speed.value.get() or "" in self.loop_value.get() or "" in self.distance_value.get():
            self.send_to_motor["state"] ="disable"
        else:
            self.send_to_motor["state"] = "active"


    def start_stream(self):
        global frame_exist
        if frame_exist == False:
            self.AddFrame()
            frame_exist = True
        self.btn_start_stream["state"] = "disable"
        self.serial_thread = threading.Thread(target=self.serial.read_serial,args= (self,), daemon=False)
        self.serial_thread.start()
        print("Starting the stream")
        if self.distance or self.force or self.time:
            pass

    def toggle_stream(self):
        if self.btn_pause_stream["text"] in "Pause":
            print("Pausing the stream")
            self.stop_stream()
            print("Paused")
            self.btn_pause_stream["text"] = "Resume"
            self.save_check["state"]= "active"
        else:
            print("Resuming the stream")
            self.start_stream()
            print("Resumed")
            self.btn_pause_stream["text"] = "Pause"
            self.save_check["state"]= "disable"

    def animate(self, distance, force, time):
        
        if self.force_distance.get() == 1:
            self.graph.clear()  # Clear the previous plot
            self.graph.set_xlabel('Distance (mm)')
            self.graph.set_ylabel('Force (N)')
            self.graph.set_title('Force vs Distance')
            self.graph.plot(distance, force, color='blue')
            self.graph_canvas.draw()

        elif self.force_time.get() == 1:
            self.graph.clear()  # Clear the previous plot
            self.graph.set_xlabel('Time (s)')
            self.graph.set_ylabel('Force (N)')
            self.graph.set_title('Force vs Time')
            self.graph.plot(time, force, color='blue')
            self.graph_canvas.draw()

        elif self.distance_time.get() == 1:
            self.graph.clear()  # Clear the previous plot
            self.graph.set_xlabel('Time (s)')
            self.graph.set_ylabel('Distance (mm)')
            self.graph.set_title('Distance vs Time')
            self.graph.plot(time, distance, color='blue')
            self.graph_canvas.draw()

    def AddFrame(self):
        self.frame_graph = LabelFrame(self.frame, text="Display Manager", padx=5, pady=5, bg="white")
        self.frame_graph.grid(padx=5, column=0, row=25, columnspan=9, sticky=NW)
        self.root.geometry("1200x600")

        self.fig = plt.Figure(figsize=(7, 5), dpi=70)
        self.graph = self.fig.add_subplot(111)  # Create subplot once

        self.graph.set_xlabel('Distance (mm)')
        self.graph.set_ylabel('Force (N)')
        self.graph.set_title('Force vs Distance')

        self.graph.plot([], [], color='blue')  # Plot empty data initially

        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2Tk(self.graph_canvas, self.frame_graph)
        self.toolbar.update()

    
    def stop_stream(self):
        self.serial.stop_read()

    def save_data(self):
        with open("Result.csv","w",newline='') as f: #appends data into file
            self.writer=csv.writer(f,delimiter=",")
            self.writer.writerow(['Force','Distance','Time'])
            rows=zip(self.force, self.distance, self.time) #allows you to save data into columns in csv file
            for row in rows:
                self.writer.writerow(row) #writes data into csv file

    
if __name__ == "__main__":
    root = RootGUI()
    serial = SerialCtrl()
    graph_widget = tk.Toplevel()
    ComGui(root, serial)
    ConnGUI(root,serial)
    mainloop()
