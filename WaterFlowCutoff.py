# -*- coding: utf-8 -*-
"""
Created on Wed May 21 11:11:59 2025

@author: Zakary.Gruber

The following code is to control the water cooling systems and prevent leaks included with a graphical user interface

"""
import random as rand

## importing GUI system
from dearpygui import dearpygui as dpg
dpg.create_context()

#import time (for delay)
import time

#import date (for information on shutdowns)
import datetime
import threading

global current_tolerance
global last_shutoff_date
global current_status
global ignore_threshold
ignore_threshold = False
last_shutoff_date = "No shutoff recorded"
current_status = "Deactivated"
current_tolerance = 1.6

sensor_differences = []  # Stores real-time difference values
time_stamps = []  # Tracks timestamps for the x-axis

# Sensor simulation (replace with actual sensor readings)

"""
These Readings need to be live from the flow meters
"""
sensor1 = 10
sensor2 = 8

duration_threshold = 10  # seconds
start_time = None

# Function to monitor sensor values without altering GUI structure
def monitor_sensor_values():
    global last_shutoff_date, start_time, current_status, ignore_threshold, current_tolerance, sensor_differences, time_stamps
    
    while True:
        if ignore_threshold:
            time.sleep(0.5)
            continue
        
        difference = abs(sensor1 - sensor2)
        
        # Store difference and timestamp for graphing
        sensor_differences.append(difference)
        time_stamps.append(time.time() - start_time if start_time else 0)
        
        if len(sensor_differences) > 100:  # Limit stored data to improve performance
            sensor_differences.pop(0)
            time_stamps.pop(0)
        
        if difference > current_tolerance:
            if start_time is None:
                start_time = time.time()
            
            elapsed_time = time.time() - start_time
            
            if elapsed_time >= duration_threshold:
                last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_status = "Deactivated"
            
                dpg.set_value("main status info", f"Current status: {current_status}")
                dpg.set_value("main shutoff info", f"System shutoff recorded at: {last_shutoff_date}") 
                
                start_time = None  # Reset timer after shutoff
        
        else:
            start_time = None
        
        time.sleep(0.5)  # Adjust polling frequency


# Start monitoring in a separate thread
monitor_thread = threading.Thread(target=monitor_sensor_values, daemon=True)
monitor_thread.start()

def reset_ignore_threshold():
    global ignore_threshold
    ignore_threshold = False

"""
Primary Window: contains links to Control Panel and Graphs as well as Warnings, current system status, and date/time of
last shutoff
"""
with dpg.window(tag= "primary window"):
    dpg.add_text("INFORMATION AND NAVIGATION")
    
    ##Button Functions
    def visit_control_panel():
        dpg.show_item("Control_Panel")
        
    def visit_graph_panel():
        dpg.show_item("Graph_Panel")
   
    #button labeling
    dpg.add_text( f"Last Shutoff: {last_shutoff_date}", tag = "main shutoff info")
    dpg.add_text(f"Current status: {current_status}", tag = "main status info")
    # dpg.add_text("Current Warnings: No current warnings")
    
    #button positioning
    with dpg.group(horizontal = True):
        dpg.add_button(label = "Control Panel", callback = visit_control_panel)
        dpg.add_button(label = "Graph Panel", callback = visit_graph_panel)

#default x and y positions
initial_x, initial_y = dpg.get_item_pos("primary window")

"""
Control Panel: contains ON button (to allow waterflow), OFF button (to stop waterflow)
as well as a tolerance (in mA) set by the user (default is based on the first production of this system)
"""
with dpg.window(tag="Control_Panel", label = "CONTROL PANEL", width = 200, show = False):
    dpg.add_text("Control Panel")
    
    ##Button Functions
    def on_button_activation():
        global current_status, ignore_threshold
        current_status = "System Active"
        dpg.set_value("main status info", f"Current status: {current_status}")
    
        # Ignore threshold checking for 10 seconds
        ignore_threshold = True
        threading.Timer(10, reset_ignore_threshold).start()
        
    
    def off_button_activation():
        current_status = "Deactivated"
        dpg.set_value("main status info", f"Current status: {current_status}")
        
        last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dpg.set_value("main shutoff info", f"System shutoff recorded at: {last_shutoff_date}")
    
    def set_tolerance():
        dpg.show_item("Set_Tolerance")
    
    #button labeling
    dpg.add_button(label = "ON", callback = on_button_activation)
    dpg.add_button(label = "OFF", callback = off_button_activation)
    dpg.add_text(f"Current Tolerance: {current_tolerance}", tag = "current_tolerance_2")
    dpg.add_button(label = "Set a new tolerance", callback = set_tolerance)

#positioning
dpg.set_item_pos("Control_Panel", [initial_x + 10, initial_y + 135])
    
"""
Set Tolerance: Displays current tolerance, has a text box for the user to set a new tolerance in mA
"""
input_field_tag = "user_input"

def update_tolerance(sender, app_data):
    global current_tolerance  # Ensure updates affect global variable
    user_tolerance = dpg.get_value(input_field_tag)  # Get user input
    
    try:
        new_tolerance = float(user_tolerance)  # Convert input to float
        current_tolerance = new_tolerance  # Update global variable
        
        # Update GUI elements dynamically
        dpg.set_value("output_text", "Success")
        dpg.set_value("current_tolerance_text", f"Current Tolerance: {current_tolerance}")
        dpg.set_value("current_tolerance_2", f"Current Tolerance: {current_tolerance}")
    
    except ValueError:
        dpg.set_value("output_text", "Error: please input a valid float")


with dpg.window(tag="Set_Tolerance", label="SET TOLERANCE", width = 250, show=False):
    dpg.add_text("Set Tolerance")
    dpg.add_text(f"Current tolerance: {current_tolerance}", tag="current_tolerance_text")  # Initially empty, updates when tolerance changes
    dpg.add_text("Set a new tolerance?")
    
    input_field = dpg.add_input_text(tag=input_field_tag)
    dpg.add_button(label="Submit", callback=update_tolerance)
    dpg.add_text("", tag="output_text")  # For success/error messages

#positioning
dpg.set_item_pos("Set_Tolerance", [initial_x + 20, initial_y + 290])
"""
Graph Panel: contains graphs for Inflow rate, Outflow rate, and current difference (between inflow and outflow)
as well as a button that updates the graph to be live(upon button press)
"""
with dpg.window(tag="Graph_Panel", label="GRAPHS", width=550, height=380, show=False):
    dpg.add_text("Graphs")

    def update_graph():
        global sensor_differences, time_stamps
        dpg.set_value(series_id, [time_stamps, sensor_differences])  # Update graph dynamically
    
    with dpg.plot(label="Difference Over Time", height=300, width=500) as plot:
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", parent=plot)
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Difference (mA)", parent=plot)
        dpg.add_plot_legend()

        dpg.set_axis_limits(y_axis, -5, 5)
        # dpg.set_axis_limits(x_axis, 0, 10)

        series_id = dpg.add_line_series([], [], label="Sensor Difference", parent=y_axis)
        
    # Button to update the graph
    dpg.add_button(label="Update Graph", callback=update_graph)




#positioning
dpg.set_item_pos("Graph_Panel", [initial_x + 280, initial_y + 10])

## Key display functions
#viewport
dpg.create_viewport(title="Water Flow Monitor", width = 1000, height = 600)
dpg.set_primary_window("primary window", True)


#finalize and show app window
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()

#cleanup
dpg.destroy_context()