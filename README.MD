### Project - System Monitor
#### Desscription 
System monitor is desktop application with a dash board to show system info, diskutilization, cpu details, memory details, wifi ssid details, load average and network speed.
##### Used frame works:
- python
- matplotlib (Graphs)
- tkinter (GUI)

##### Python and dependent module steps:
- Download and install python 3.X from "https://www.python.org/downloads/"
- Check installtion status using "python -v" command in command prompt
- Install pip from "https://phoenixnap.com/kb/install-pip-windows"
- Install all dependecy modules using "pip install 'module name'" syntax, below are required examples, it will ignore if module already exists.
	- pip install tkinter
	- pip install psutil
	- pip install platform
	- pip install matplotlib
	- pip install numpy
	- pip install collections
	- pip install jproperties
	
	
##### Run commands:
- open command prompt in root directory
- run "python system_monitor.py"


### Used Matplotlib graphs
- Bar chart :  Disk utilization, Memory utilization
- line(plot) graph : Network traffic, CPU utilization, load average
- Horizontal bar chart : Internet signals

### Used modules for each tab
#### System Info
- Used platform module to get information about the system
- Displayed information as part tkinter labels

#### Disk Utilization
- Used "psutil.disk_usage(part.mountpoint)" , "part.device" to get set of disks and usage details.
- Added above information to matplot bar chart using "disk_ax_arr.bar(indicator, used_GB, width, color='r')" to display graph
- Repeated above steps in loop for all avaialble disks.

#### Network Traffic
- Used "net_io_counters()" from psutil module to get network upload and downlaod bytes information
- Collected above counters in queue to maintain last 20 seconds data.
- Added above queue to matplot plot "network_usage_ax.plot(upload_bytes_queue, label='Total Uplaod', color='g', antialiased=True)" line graph
- plotted scatter dot to highlight the latest entry used "network_usage_ax.scatter(len(upload_bytes_queue) - 1, upload_bytes_queue[-1])"
- Repeated above steps for all upload and download bytes data.

#### CPU Utilization
- Used "psutil.cpu_percent()" from psutil module to get usage details.
- maintained above data in queue for last 30 seconds
- Added above data to "cpu_ax.plot([index,index + 1],[previousValue, curentValue],color=cpu_graph_color)" to plot each line.
	- if cpu percentage is above threshold value this line drawn in red color else it is in green
- Collected and displayed current process and cpu cores using "psutil.pids()" and "psutil.cpu_count()"
- Collected and diplayed up time using "current time - psutil.boot_time()"

#### Memory Utilization
- Collected ram usage deatils using "psutil.virtual_memory()" from psutil module.
- Displayed above deatils using "mem_usage_ax.bar(mem_legends[0], mem_values[0], color='maroon', width=0.4)" in bar graph.

#### Load Average
- Used "load1, load5, load15 = psutil.getloadavg()" to get the load deatils of 1min, 5min and 15 respectivly
- Maintained above data in queue to display last 20 seconds.
- Used "load_avg_ax.plot(load_avg_1_min_queue, label='1 min', color='g', antialiased=True)" to plot line graph

#### Internet Signal
- Used "netsh wlan show networks mode=BSSID" command to get list available wifi networks and signal strengths.
	- NOTE: this command gives the list in cash of waln adapter, it wont scan the card to list, to get refreshed data we can open wifi panel
- Parsed above information and displayed using "internet_signal_ax.barh(ssid_names, ssid_signal_strength,height = 0.4)" in horizontal bar chart.