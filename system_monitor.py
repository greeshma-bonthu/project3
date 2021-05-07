import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import os
import sys
import shutil
import subprocess
from collections import deque
import psutil
import platform,socket,re,uuid,json,logging
from psutil._common import bytes2human
from psutil import net_io_counters
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import collections
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
import math
from jproperties import Properties

from math import sin
#import matplotlib.pyplot as plt
#from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#import matplotlib.pyplot as plt
#import matplotlib as mpl
#import matplotlib.animation as animation
from collections import deque
#import numpy as np
#from matplotlib.figure import Figure

######### the followings to personalize the dimensions of the level indicators in the CPU tab
# left pad in canvas
rx1 = 10
# top pad in canvas
ry1 = 25
# width of the background rectangle
rx1_width = 80
# height of the background rectangle
ry1_height = 200
# the pad between the background rectangle
rrpad = 10
# inner rectangles
# width
rx1_in_width = 60
# height
ry1_in_height = 180

###################

# loop interval
LOOP_INTERVAL = 1000
# gpu vendor
GPU_VENDOR = ""
###########
# application name
app_name = "System Monitor"
# application width
app_width = 1200
# application height
app_height = 700
# base font size
font_size = 18
# font size for cpu usage level
font_size2 = 18
# alternate text color
frg_color = "gray40"
# background color of diagram
dia_color = "gray70"
# background color of sensors
dia_color2 = "gray80"
# width of the line
dia_width = 2

## Variables
last_upload, last_download, upload_speed, down_speed = 0, 0, 0, 0
temp_i = 0
# number of points in the diagram, one per time defined by LOOP_INTERVAL
deque_size = 30
dcpu = deque('', deque_size)
for i in range(deque_size):
    dcpu.append('0')

## maintaining CPU queue and respected timestamp to plot scatter grapgh, 30 sec
cpu_queue = collections.deque(np.zeros(30))
cpu_queue_timeStamp = collections.deque(np.empty(30, dtype='str'))
#print(cpu_queue_timeStamp)

#maintaining load average queue of 1 min, 5 min, 15 min and respected timestamp of 30 sec
load_avg_1_min_queue = collections.deque(np.zeros(30))
load_avg_5_min_queue = collections.deque(np.zeros(30))
load_avg_15_min_queue = collections.deque(np.zeros(30))
load_avg_queue_timeStamp = collections.deque(np.empty(30, dtype='str'))

#maintaining upload and download bytes, speed queue and time stamp to plot scatter graph with 20 sec time
upload_bytes_queue = collections.deque(np.zeros(20))
download_bytes_queue = collections.deque(np.zeros(20))
total_bytes_queue = collections.deque(np.zeros(20))
upload_speed_bytes_queue = collections.deque(np.zeros(20))
download_speed_bytes_queue = collections.deque(np.zeros(20))
network_queue_timeStamp = collections.deque(np.empty(20, dtype='str'))
# read and maintain key values of threshold_config.properties file
threshold_configs_dict = {}
class MonitorApplication(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        self.pack(fill="both", expand=True)
        self.master.update_idletasks()        
        self.create_menu_tab()   
        
    def create_menu_tab(self):
        # font family and size
        self.s = ttk.Style(self.master)
        self.s.configure('.', font=('', font_size))
        
        # the notebook
        self.wnb = ttk.Notebook(self, style='lefttab.TNotebook')
        self.wnb.pack(expand=True, fill="both")
        
        ### System Info
        frame0 = ttk.Frame(self)
        self.wnb.add(frame0, text="System Info")
        ## labels
        table_grid = ttk.Frame(frame0)
        table_grid.pack(side="left", anchor="n")
        # empty label
        label_empty = ttk.Label(table_grid, text="").grid(column=0, row=0)
        #Platform
        label_sys = ttk.Label(table_grid, text="System  ", foreground=frg_color).grid(column=0, row=1, sticky="NE")
        system_name = platform.system()
        label_sys_temp = ttk.Label(table_grid, text=system_name).grid(column=1, row=1, sticky="NW")
       
        
        # version
        label_version = ttk.Label(table_grid, text="Version  ", foreground=frg_color).grid(column=0, row=2, sticky="NE")
        version = platform.version()
        label_version_temp = ttk.Label(table_grid, text=version).grid(column=1, row=2, sticky="NW")
        
        # release
        label_release = ttk.Label(table_grid, text="Release  ", foreground=frg_color).grid(column=0, row=3, sticky="NE")
        release = platform.release()
        label_release_temp = ttk.Label(table_grid, text=release).grid(column=1, row=3, sticky="NW")
        
        # ram
        label_ram = ttk.Label(table_grid, text="RAM  ", foreground=frg_color).grid(column=0, row=4)
        ram = str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        label_ram_temp = ttk.Label(table_grid, text=ram).grid(column=1, row=4, sticky="NW")
        
         # host name
        label_host = ttk.Label(table_grid, text="Host Name  ", foreground=frg_color).grid(column=0, row=5, sticky="NE")
        host = socket.gethostname()
        label_host_temp = ttk.Label(table_grid, text=host).grid(column=1, row=5, sticky="NW")
        
         # ip address
        label_IP = ttk.Label(table_grid, text="IP Address  ", foreground=frg_color).grid(column=0, row=6, sticky="NE")
        ip = socket.gethostbyname(socket.gethostname())
        label_ip_temp = ttk.Label(table_grid, text=ip).grid(column=1, row=6, sticky="NW")        
         
         # mac address
        label_mac = ttk.Label(table_grid, text="Mac Address  ", foreground=frg_color).grid(column=0, row=7, sticky="NE")
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        label_mac_temp = ttk.Label(table_grid, text=mac).grid(column=1, row=7, sticky="NW")
        
         # cpu
        label_cpu = ttk.Label(table_grid, text="CPU  ", foreground=frg_color).grid(column=0, row=8, sticky="NE")
        cpu = platform.processor()
        label_cpu_temp = ttk.Label(table_grid, text=cpu).grid(column=1, row=8, sticky="NW")
        
          # cores
        label_cores = ttk.Label(table_grid, text="Cores  ", foreground=frg_color).grid(column=0, row=9, sticky="NE")
        cores = str(psutil.cpu_count())
        label_cores_temp = ttk.Label(table_grid, text=cores).grid(column=1, row=9, sticky="NW")
        
         # username
        label_user = ttk.Label(table_grid, text="User Name  ", foreground=frg_color).grid(column=0, row=10, sticky="NE")
        user_name = platform.uname()
        label_user_temp = ttk.Label(table_grid, text=user_name).grid(column=1, row=10, sticky="NW")

        # single function to read threshold_config file and store values in dictionary
        def read_threshold_config():
            configs = Properties()
            with open('threshold_config.properties', 'rb') as config_file:
                configs.load(config_file)
            items_view = configs.items()
            threshold_configs_dict.clear()
            for item in items_view:
                threshold_configs_dict[item[0]] = int(item[1].data)

        ###### tab 1 Disk Utilization ######
        frame1 = ttk.Frame(self)
        self.wnb.add(frame1, text="Disk Utilization")
        ## labels
        table_disk_grid = ttk.Frame(frame1)
        table_disk_grid.pack(side="left", anchor="n")
        
        obj_Disk = psutil.disk_usage('/')
        # empty label
        label_disk_empty = ttk.Label(table_disk_grid, text="").grid(column=0, row=0)

        #create disk figure and plots to add bar graph
        disk_fig, disk_ax_arr = plt.subplots( constrained_layout=True, figsize=(15, 15), facecolor='#DEDEDE', sharex=True, sharey=True)
        disk_canvas = FigureCanvasTkAgg(disk_fig, frame1)
        disk_canvas.get_tk_widget().pack()

        i = 2;
        width = 0.25
        #maintain the queue of returned disk names and used,free,total space details
        xTick_lables = []
        total_GB = []
        used_GB = []
        free_GB = []
        high = 0
        low = 0
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue

                usage = psutil.disk_usage(part.mountpoint)
                device = part.device
                print(device)
                xTick_lables.append(device)
                #total = bytes2human(usage.total)
                total = usage.total / float(1 << 30)
                #used = bytes2human(usage.used)
                used = usage.used / float(1 << 30)
                #free = bytes2human(usage.free)
                free = usage.free / float(1 << 30)
                usg_per = int(usage.percent)
                dev_type = part.fstype
                mount = part.mountpoint
                #print("total : " ,total)
                #print("free : ", free)
                #print("used : ", used)

                # append discovered values of disk
                total_GB.append(total)
                used_GB.append(used)
                free_GB.append(free)
                if total > high:
                    high = total
                i = i + 1
        #print(used_GB)

        indicator = np.arange(i -2)
        # adding details to plot bar graph
        disk_ax_arr.set_facecolor('#DEDEDE')
        disk_ax_arr.set_xticks(indicator + width)
        disk_ax_arr.bar(indicator, used_GB, width, color='r')
        disk_ax_arr.bar(indicator + width, free_GB, width, color='g')
        disk_ax_arr.bar(indicator + width + width, total_GB, width, color='b')
        disk_ax_arr.set_ylim([0, math.ceil(high + 0.5 * (high - low))])
        disk_ax_arr.legend(('Used', 'Free', 'Total'))
        disk_ax_arr.set_xticklabels(xTick_lables)
        disk_ax_arr.set_ylabel('Size in GB')
        disk_ax_arr.set_xlabel('Disk Mounts')
        disk_ax_arr.set_title('Disk Usage')

        #draw canvas to show graph
        disk_canvas.draw()
        
        ###### tab 2 Network Traffic ######
        frame2 = ttk.Frame(self)
        self.wnb.add(frame2, text="Network Traffic")
        
        
        REFRESH_DELAY = 1000 # Window update delay in ms.

        #createing network figure with two subplots
        network_fig = plt.figure(constrained_layout=True, figsize=(15, 15), facecolor='#DEDEDE')
        network_usage_ax = plt.subplot(121)
        network_speed_ax = plt.subplot(122)
        network_usage_ax.set_facecolor('#DEDEDE')
        network_speed_ax.set_facecolor('#DEDEDE')
        network_canvas = FigureCanvasTkAgg(network_fig, frame2)
        network_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)
        # Updating Labels
        def update_network():
            global last_upload, last_download, upload_speed, down_speed
            counter = net_io_counters()

            upload = counter.bytes_sent
            download = counter.bytes_recv
            total = upload + download

            if last_upload > 0:
                if upload < last_upload:
                    upload_speed = 0
                else:
                    upload_speed = upload - last_upload

            if last_download > 0:
                if download < last_download:
                    down_speed = 0
                else:
                    down_speed = download - last_download

            last_upload = upload
            last_download = download

            # converting bytes to MB and queueing in respected collection
            upload_bytes_queue.popleft()
            upload_bytes_queue.append(upload / float(1 << 20))
            download_bytes_queue.popleft()
            download_bytes_queue.append(download / float(1 << 20))
            total_bytes_queue.popleft()
            total_bytes_queue.append(total / float(1 << 20))
            #queueing timestamps
            network_queue_timeStamp.popleft()
            network_queue_timeStamp.append(datetime.now().strftime("%H:%M:%S"))
            #clear previous graph
            network_usage_ax.clear()

            #plot scatter graph with queued data of upload, download,total bytes
            network_usage_ax.plot(upload_bytes_queue, label='Total Uplaod', color='g', antialiased=True)
            network_usage_ax.scatter(len(upload_bytes_queue) - 1, upload_bytes_queue[-1])
            network_usage_ax.plot(download_bytes_queue, label='Total Download', color='r', antialiased=True)
            network_usage_ax.scatter(len(download_bytes_queue) - 1, download_bytes_queue[-1])
            network_usage_ax.plot(total_bytes_queue, label='Total Usage', color='b', antialiased=True)
            network_usage_ax.scatter(len(total_bytes_queue) - 1, total_bytes_queue[-1])
            network_usage_ax.set_xticks(np.arange(0, 20, 1))
            network_usage_ax.set_xticklabels(network_queue_timeStamp, rotation=45)
            #network_usage_ax.set_xlabel('Time', fontstyle='italic')
            network_usage_ax.set_ylabel('Usage in MB', fontstyle='italic')
            network_usage_ax.set_title('Network Usage')
            network_usage_ax.grid(linewidth=0.4, antialiased=True)
            network_usage_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fancybox=True, shadow=True)
            network_usage_ax.autoscale(True)
            network_usage_ax.set_facecolor('#DEDEDE')

            # converting bytes to KB and queueing in respected collection
            upload_speed_bytes_queue.popleft()
            upload_speed_bytes_queue.append(upload_speed / float(1<<10))
            download_speed_bytes_queue.popleft()
            download_speed_bytes_queue.append(down_speed / float(1<<10))

            #clear previous graph
            network_speed_ax.clear()

            #scatter plot upload and download speed
            network_speed_ax.plot(upload_speed_bytes_queue, label='Upload Speed', color='g', antialiased=True)
            network_speed_ax.scatter(len(upload_speed_bytes_queue) - 1, upload_speed_bytes_queue[-1])
            network_speed_ax.plot(download_speed_bytes_queue, label='Download Speed', color='r', antialiased=True)
            network_speed_ax.scatter(len(download_speed_bytes_queue) - 1, download_speed_bytes_queue[-1])
            network_speed_ax.set_xticks(np.arange(0, 20, 1))
            network_speed_ax.set_xticklabels(network_queue_timeStamp, rotation=45)
            #network_speed_ax.set_xlabel('Time', fontstyle='italic')
            network_speed_ax.set_ylabel('Speed in KB', fontstyle='italic')
            network_speed_ax.set_title('Network Speed')
            network_speed_ax.grid(linewidth=0.4, antialiased=True)
            network_speed_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fancybox=True, shadow=True)
            network_speed_ax.autoscale(True)
            network_speed_ax.set_facecolor('#DEDEDE')

            #draw canvas to show graphs
            network_canvas.draw()
            
            frame2.after(REFRESH_DELAY, update_network)  # reschedule event in refresh delay.

        frame2.after(REFRESH_DELAY, update_network)
        
        ###### tab 3 CPU utilization ######
        frame3 = ttk.Frame(self)
        self.wnb.add(frame3, text="CPU utilization")

        cpu_fig, cpu_ax = plt.subplots(constrained_layout=True, figsize=(15, 15),facecolor='#DEDEDE')
        # define and adjust figure
        #fig = plt.figure(facecolor='#DEDEDE')
        #ax = plt.subplot(121)
        cpu_ax.set_facecolor('#DEDEDE')
        canvas = FigureCanvasTkAgg(cpu_fig, frame3)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)
        # animate

        def update_cpu_usage():
            read_threshold_config()
            global temp_i
            #cpu = psutil.cpu_percent(4)
            #label_cpu_usage_value["text"] = cpu
            #label_cpu_usage_value.pack()


            #maintain current cpu values in queue
            cpu_queue.popleft()
            cpu_percent = psutil.cpu_percent()


            cpu_queue.append(cpu_percent)
            cpu_queue_timeStamp.popleft()
            cpu_queue_timeStamp.append(datetime.now().strftime("%H:%M:%S"))


            #clear previous graph
            cpu_ax.clear()

            #scatter plot cpu usage graph
            index = 0
            #for previousValue,curentValue, nextValue in zip(list(cpu_queue),list(cpu_queue)[1:], list(cpu_queue)[2:]):
            for previousValue, curentValue in zip(list(cpu_queue),list(cpu_queue)[1:]):
                # alret and color change during greater threshold value
                if curentValue > threshold_configs_dict["CPU_USAGE_THRESHOLD"]:
                    cpu_graph_color = "red"
                    # alert dialog box
                   #messagebox.showinfo("Cpu Usage", "cpu usage beyond threshold")
                else:
                    cpu_graph_color = "green"
                #plotting each ine
                cpu_ax.plot([index,index + 1],[previousValue, curentValue],color=cpu_graph_color)
                index+= 1



            cpu_ax.text(len(cpu_queue) - 1, cpu_queue[-1] + 2, "{}%".format(cpu_queue[-1]))
            cpu_ax.set_xticks(np.arange(0, 30, 1))

            cpu_ax.set_xticklabels(cpu_queue_timeStamp,rotation = 45)

            cpu_ax.set_title('CPU %\n')
            cpu_ax.set_ylim(0, 120)
            ## displaying cores, uptime, process count details
            cpu_ax.text(1, 120, 'Processes : ' + str(len(psutil.pids())) , size=15, color='#083FE3')
            cpu_ax.text(1, 115, 'CPU Cores : ' + str(psutil.cpu_count()), size=15, color='#083FE3')
            BootTime = datetime.fromtimestamp(psutil.boot_time()).strftime("%d:%H:%M:%S")
            currentTime = datetime.now().strftime("%d:%H:%M:%S")
            up_time = (datetime.strptime(currentTime, '%d:%H:%M:%S') - datetime.strptime(BootTime,'%d:%H:%M:%S'))
            cpu_ax.text(1, 110,'Up time : ' + str(up_time), size=15, color='#083FE3')
            #cpu_ax.text(1, 105, f'thread count per core: {psutil.cpu_count() // psutil.cpu_count(logical=False)}', size=15, color='#083FE3')
            # remove spines
            cpu_ax.spines['left'].set_visible(False)
            cpu_ax.spines['right'].set_visible(False)
            cpu_ax.spines['top'].set_visible(False)
            canvas.draw()


            frame3.after(REFRESH_DELAY, update_cpu_usage)
        frame3.after(REFRESH_DELAY, update_cpu_usage)

        ###### tab 4 Memory utilization ######
        frame4 = ttk.Frame(self)
        self.wnb.add(frame4, text="Memory Utilization")

        #create memory figure and two subplots to plot graphs
        mem_fig = plt.figure(figsize=(12, 6), facecolor='#DEDEDE')
        mem_usage_ax = plt.subplot(121)
        mem_per_ax = plt.subplot(122)
        mem_per_ax.set_facecolor('#DEDEDE')
        mem_legends = ['Available', 'Used']
        mem_values = [0, 0]

        mem_canvas = FigureCanvasTkAgg(mem_fig, frame4)
        mem_canvas.get_tk_widget().pack()

        
        def update_ram_usage():
            #read config file to get latest threshold values
            read_threshold_config()
            #clear previous graph
            mem_usage_ax.clear()
            low = min(mem_values)
            high = max(mem_values)

            #get current ram usage details
            mem_values[0]=round(psutil.virtual_memory().available/(1024.0**3),2)
            mem_values[1]=round(psutil.virtual_memory().used/(1024.0**3),2)

            #plot bar graph of ram usage
            mem_usage_ax.set_title('RAM Details')
            if(low != high):
                mem_usage_ax.set_ylim([0, 1.50 * high])

            mem_usage_ax.bar(mem_legends[0], mem_values[0], color='g', width=0.4)
            mem_usage_ax.bar(mem_legends[1], mem_values[1], color='maroon', width=0.4)
            mem_usage_ax.set_ylabel('GB')
            mem_usage_ax.set_facecolor('#DEDEDE')

            # clear previous graph
            mem_per_ax.clear()

            # current time and ram percentage used
            dateTimeObj = datetime.now()
            mem_per_ax.set_ylim([0, 100])
            mem_usage_value =  psutil.virtual_memory()[2]

            #alert beyond threshold values
            if mem_usage_value > threshold_configs_dict['MEMORY_USAGE_THRESHOLD']:
                memory_graph_color = "#9C260D"
                messagebox.showinfo("Memory Usage", "Memory usage beyond threshold")
            else:
                memory_graph_color = "#083FE3"
            mem_per_ax.set_title('RAM Usage')
            mem_per_ax.bar(dateTimeObj.strftime("%H:%M:%S"),mem_usage_value, color=memory_graph_color, width=0.4)
            #draw canvas to show graph
            mem_canvas.draw()
            frame4.after(REFRESH_DELAY, update_ram_usage)
        frame4.after(REFRESH_DELAY, update_ram_usage)

        
        ###### tab 5 Load Averages ######
        frame5 = ttk.Frame(self)
        self.wnb.add(frame5, text="Load Averages")

        #creating load average figure and plot
        load_avg_fig, load_avg_ax = plt.subplots(constrained_layout=True, facecolor='#DEDEDE',figsize=(15, 15))

        load_avg_ax.set_facecolor('#DEDEDE')
        load_avg_canvas = FigureCanvasTkAgg(load_avg_fig, frame5)
        load_avg_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

        def update_cpu_load_avg():
            #use diffrent approch get load average details as per OS
            if platform.system() == "Linux" :
                load1, load5, load15 = os.getloadavg()
            elif platform.system() == "Windows":
                load1, load5, load15 = psutil.getloadavg()

            #Queue all load average details
            load_avg_1_min_queue.popleft()
            load_avg_1_min_queue.append(load1)
            load_avg_5_min_queue.popleft()
            load_avg_5_min_queue.append(load5)
            load_avg_15_min_queue.popleft()
            load_avg_15_min_queue.append(load15)
            #queue respected time stamp details
            load_avg_queue_timeStamp.popleft()
            load_avg_queue_timeStamp.append(datetime.now().strftime("%H:%M:%S"))
            #clear previous graph
            load_avg_ax.clear()
            #scatter plot load average data
            load_avg_ax.plot(load_avg_1_min_queue, label='1 min', color='g', antialiased=True)
            load_avg_ax.scatter(len(load_avg_1_min_queue) - 1, load_avg_1_min_queue[-1])
            load_avg_ax.plot(load_avg_5_min_queue, label='5 min', color='r', antialiased=True)
            load_avg_ax.scatter(len(load_avg_5_min_queue) - 1, load_avg_5_min_queue[-1])
            load_avg_ax.plot(load_avg_15_min_queue, label='15 min', color='b',antialiased=True)
            load_avg_ax.scatter(len(load_avg_15_min_queue) - 1, load_avg_15_min_queue[-1])
            load_avg_ax.set_xticks(np.arange(0, 30, 1))
            load_avg_ax.set_xticklabels(load_avg_queue_timeStamp, rotation=45)
            #load_avg_ax.set_xlabel('Time', fontstyle='italic')
            load_avg_ax.set_ylabel('Load average', fontstyle='italic')
            load_avg_ax.set_title('Load average graph')
            load_avg_ax.grid(linewidth=0.4, antialiased=True)
            load_avg_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fancybox=True, shadow=True)
            load_avg_ax.autoscale(True)
            load_avg_ax.set_facecolor('#DEDEDE')
            load_avg_canvas.draw()
            frame5.after(REFRESH_DELAY, update_cpu_load_avg)

        frame5.after(REFRESH_DELAY, update_cpu_load_avg)
        
        ###### tab 6 Internet Signal ######
        frame6 = ttk.Frame(self)
        self.wnb.add(frame6, text="Internet Signal")

        #Creating figure and graph to list wifi ssid name and signal strength
        inetrnet_signal_fig, internet_signal_ax = plt.subplots(constrained_layout=True, facecolor='#DEDEDE', figsize=(15, 15))
        internet_signal_ax.set_facecolor('#DEDEDE')
        internet_signal_canvas = FigureCanvasTkAgg(inetrnet_signal_fig, frame6)
        internet_signal_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

        def update_internet_signal():
            #get wifi networks data using netsh command
            #NOTE: this command gives the list in cash of waln adapter, it wont scan the card to list, to get refreshed data we can open wifi panel

            networkProc = subprocess.run(["netsh", "wlan", "show", "networks", "mode=Bssid"], text=True,shell=True,capture_output=True)
            result = subprocess.run(["Findstr" "/R", "\<SSID\> \<Signal\>"],
                              input=networkProc.stdout, capture_output=True,
                               text=True,shell=True).stdout
            #parse command output and create a list with names and signal strength
            stdout = result
            #print(stdout)
            ls = stdout.split("\n")
            ssid_names = []
            ssid_signal_strength = []

            length = len(ls)
            index = 0
            isErrorOccured = False
            for line in ls:
                if 'SSID' in line.split(" "):
                    ssid_names.append(line.split(":")[1].strip())
                    if (index + 1) < length and 'SSID' in ls[index + 1].split(" "):
                        ssid_signal_strength.append(0)
                        isErrorOccured = True
                if 'Signal' in line.split(" "):
                    if 'Signal' not in ls[index - 1].split(" "):
                        ssid_signal_strength.append(int(line.split(":")[1].strip().replace("%", "")))
                    else:
                        isErrorOccured = True
                index = index + 1
            if len(ssid_names) != len(ssid_signal_strength):
                ssid_signal_strength.append(0)
                isErrorOccured = True
                #print("added outer")
            #if isErrorOccured:
                #print("***************************************************")
                #print(stdout)
                #print("***************************************************")
                #print(ssid_names)
                #print(ssid_signal_strength)
            #clear previous graph
            internet_signal_ax.clear()
            #plot horizontal bar graph
            #internet_signal_ax.grid(True)
            internet_signal_ax.margins(0.05)

            internet_signal_ax.barh(ssid_names, ssid_signal_strength,height = 0.4)
            internet_signal_ax.set_title('Internet Signal')
            internet_signal_ax.set_ylabel('SSID')
            internet_signal_ax.set_xlabel('Signal Strength')
            internet_signal_ax.set_yticklabels(ssid_names, rotation=45)
            if len(ssid_names) < 5:
                internet_signal_ax.set_ylim(-0.5, 5)
            else :
                internet_signal_ax.set_ylim(-0.5, len(ssid_names) + 1)
            internet_signal_ax.set_xlim(0, 100)

            #draw canvas to show graph
            internet_signal_canvas.draw()
            frame6.after(REFRESH_DELAY, update_internet_signal)

        frame6.after(REFRESH_DELAY, update_internet_signal)

        
        #window.mainloop()

# Variables for use in the size() function.
KB = float(1024)
MB = float(KB ** 2) # 1,048,576
GB = float(KB ** 3) # 1,073,741,824
TB = float(KB ** 4) # 1,099,511,627,776
def size(B):
	B = float(B)
	if B < KB: return f"{B} Bytes"
	elif KB <= B < MB: return f"{B/KB:.2f} KB"
	elif MB <= B < GB: return f"{B/MB:.2f} MB"
	elif GB <= B < TB: return f"{B/GB:.2f} GB"
	elif TB <= B: return f"{B/TB:.2f} TB"
def main():
    root = tk.Tk()
    root.title(app_name)
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    width = app_width
    height = app_height
    root.geometry('{}x{}'.format(width, height))
    
    # style
    s = ttk.Style()
    s.theme_use("clam")
    #s.configure('lefttab.TNotebook', tabposition='ws')
    app = MonitorApplication(master=root)
    app.mainloop()
    
if __name__ == "__main__":
    main()