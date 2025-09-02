# -*- coding: utf-8 -*-
"""
Created on Thu May 22 13:49:59 2025

@author: Zakary.Gruber
"""

import random as rand
from dearpygui import dearpygui as dpg
import time
import datetime
import threading

dpg.create_context()

global current_tolerance, last_shutoff_date, current_status, ignore_threshold
ignore_threshold = False
last_shutoff_date = "No shutoff recorded"
current_status = "Deactivated"
current_tolerance = 1.6

sensor_differences = []
time_stamps = []
sensor1 = 10
sensor2 = 8
duration_threshold = 10
start_time = None

# Sensor simulation
def simulate_sensor_values():
    global sensor1, sensor2
    while True:
        sensor1 = rand.uniform(4, 20)
        if rand.random() < 0.9:
            sensor2 = sensor1 + rand.uniform(-1.6, 1.6)
        else:
            sensor2 = sensor1 + rand.uniform(-3.0, 3.0)

        sensor2 = max(4, min(20, sensor2))
        time.sleep(0.5)

sensor_simulation_thread = threading.Thread(target=simulate_sensor_values, daemon=True)
sensor_simulation_thread.start()

def monitor_sensor_values():
    global last_shutoff_date, start_time, current_status, ignore_threshold, sensor_differences, time_stamps

    while True:
        difference = abs(sensor1 - sensor2)

        if not ignore_threshold:
            sensor_differences.append(difference)
            time_stamps.append(time.time())

            if len(sensor_differences) > 100:
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
                
                start_time = None

        else:
            start_time = None

        time.sleep(0.5)

monitor_thread = threading.Thread(target=monitor_sensor_values, daemon=True)
monitor_thread.start()

def reset_ignore_threshold():
    global ignore_threshold
    ignore_threshold = False

# Primary Window with Tabs
with dpg.window(tag="primary window"):
    dpg.add_text("INFORMATION AND NAVIGATION")
    dpg.add_text(f"Last Shutoff: {last_shutoff_date}", tag="main shutoff info")
    dpg.add_text(f"Current status: {current_status}", tag="main status info")

    with dpg.tab_bar():
        with dpg.tab(label="Control Panel"):
            dpg.add_text("Control Panel")

            def on_button_activation():
                global current_status, ignore_threshold
                current_status = "System Active"
                dpg.set_value("main status info", f"Current status: {current_status}")

                ignore_threshold = True
                threading.Timer(10, reset_ignore_threshold).start()

            def off_button_activation():
                global current_status
                current_status = "Deactivated"
                dpg.set_value("main status info", f"Current status: {current_status}")

                last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                dpg.set_value("main shutoff info", f"System shutoff recorded at: {last_shutoff_date}")

            dpg.add_button(label="ON", callback=on_button_activation)
            dpg.add_button(label="OFF", callback=off_button_activation)
            dpg.add_text(f"Current Tolerance: {current_tolerance}", tag="current_tolerance_2")
        
        with dpg.tab(label="Set Tolerance"):
            dpg.add_text("Set Tolerance")
            dpg.add_text(f"Current tolerance: {current_tolerance}", tag="current_tolerance_text")

            input_field_tag = "user_input"
            def update_tolerance(sender, app_data):
                global current_tolerance
                user_tolerance = dpg.get_value(input_field_tag)

                try:
                    new_tolerance = float(user_tolerance)
                    current_tolerance = new_tolerance

                    dpg.set_value("current_tolerance_text", f"Current Tolerance: {current_tolerance}")
                    dpg.set_value("current_tolerance_2", f"Current Tolerance: {current_tolerance}")
                    dpg.set_value("output_text", "Success")

                except ValueError:
                    dpg.set_value("output_text", "Error: please input a valid float")

            dpg.add_input_text(tag=input_field_tag)
            dpg.add_button(label="Submit", callback=update_tolerance)
            dpg.add_text("", tag="output_text")

        with dpg.tab(label="Graph Panel"):
            dpg.add_text("Graphs")
            series_id = None

            def update_graph():
                global series_id, sensor_differences, time_stamps

                current_time = time.time()
                filtered_differences = []
                filtered_timestamps = []

                for i in range(len(time_stamps)):
                    elapsed_time = current_time - time_stamps[i]
                    if elapsed_time <= 10:
                        filtered_differences.append(sensor_differences[i])
                        filtered_timestamps.append(elapsed_time)

                if series_id and filtered_timestamps and filtered_differences:
                    dpg.set_value(series_id, [filtered_timestamps, filtered_differences])

            def auto_update_graph():
                while True:
                    update_graph()
                    time.sleep(1)

            graph_update_thread = threading.Thread(target=auto_update_graph, daemon=True)
            graph_update_thread.start()

            with dpg.plot(label="Difference Over Time", height=300, width=500) as plot:
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", parent=plot)
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Difference (mA)", parent=plot)
                dpg.add_plot_legend()

                dpg.set_axis_limits(y_axis, 0, 5)
                dpg.set_axis_limits(x_axis, 0, 10)

                series_id = dpg.add_line_series([], [], label="Sensor Difference", parent=y_axis)

            dpg.add_button(label="Update Graph", callback=update_graph)

dpg.create_viewport(title="Water Flow Monitor", width=550, height=500)
dpg.set_primary_window("primary window", True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()

dpg.destroy_context()
