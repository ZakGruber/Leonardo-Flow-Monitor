# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 11:45:53 2025

@author: Zakary.Gruber
"""

import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import messagebox
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
SENSOR1_PIN = 17  # Example GPIO pin for sensor 1
SENSOR2_PIN = 18  # Example GPIO pin for sensor 2

GPIO.setup(SENSOR1_PIN, GPIO.IN)
GPIO.setup(SENSOR2_PIN, GPIO.IN)

PULSES_PER_GALLON = 2840

# Initialize global variables
ignore_threshold = False
last_shutoff_date = "No shutoff recorded"
current_status = "Deactivated"
current_tolerance = 1.6

sensor_differences = []
time_stamps = []
flow_count1 = 0
flow_count2 = 0
duration_threshold = 10
start_time = None

# Interrupt handler to count pulses
def pulse_detected1(channel):
    global flow_count1
    flow_count1 += 1

def pulse_detected2(channel):
    global flow_count2
    flow_count2 += 1

GPIO.add_event_detect(SENSOR1_PIN, GPIO.RISING, callback=pulse_detected1)
GPIO.add_event_detect(SENSOR2_PIN, GPIO.RISING, callback=pulse_detected2)

# Function to update labels
def update_labels():
    status_label.config(text=f"Current status: {current_status}")
    shutoff_label.config(text=f"System shutoff recorded at: {last_shutoff_date}")

# Function to monitor sensor values (Runs before updating graph)
def monitor_sensor_values():
    global last_shutoff_date, start_time, current_status, ignore_threshold
    global sensor_differences, time_stamps, flow_count1, flow_count2
    
    rate1 = flow_count1 / PULSES_PER_GALLON
    rate2 = flow_count2 / PULSES_PER_GALLON
    flow_count1 = 0
    flow_count2 = 0

    difference = abs(rate1 - rate2)

    if not ignore_threshold:
        sensor_differences.append(difference)
        time_stamps.append(time.time())

        # Limit history size
        if len(sensor_differences) > 100:
            sensor_differences.pop(0)
            time_stamps.pop(0)

    # Shutoff logic
    if difference > current_tolerance:
        if start_time is None:
            start_time = time.time()

        elapsed_time = time.time() - start_time
        if elapsed_time >= duration_threshold:
            last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_status = "Deactivated"
            update_labels()
            start_time = None
    else:
        start_time = None

    # Call graph update **after sensor values are processed**
    root.after(1000, update_graph)

# Function to update graph
def update_graph():
    global time_stamps, sensor_differences

    if time_stamps and sensor_differences and len(time_stamps) == len(sensor_differences):
        # Normalize timestamps relative to the first recorded time
        normalized_timestamps = [t - time_stamps[0] for t in time_stamps]

        ax.clear()
        ax.plot(normalized_timestamps, sensor_differences, label="Flow Rate Difference (GPM)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Flow Rate Difference (GPM)")
        ax.legend()
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

    # Schedule next sensor read **after** graph update
    root.after(1000, monitor_sensor_values)

# GUI Setup
root = tk.Tk()
root.title("Water Flow Monitor")

# Status Labels
info_label = tk.Label(root, text="INFORMATION AND NAVIGATION", font=("Arial", 14, "bold"))
info_label.pack()

shutoff_label = tk.Label(root, text=f"System shutoff recorded at: {last_shutoff_date}")
shutoff_label.pack()

status_label = tk.Label(root, text=f"Current status: {current_status}")
status_label.pack()

# Control Panel
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Label(control_frame, text="Control Panel", font=("Arial", 12)).pack()
tk.Button(control_frame, text="ON", command=lambda: activate_system()).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="OFF", command=lambda: deactivate_system()).pack(side=tk.RIGHT, padx=5)

# Tolerance Setting
tolerance_frame = tk.Frame(root)
tolerance_frame.pack(pady=10)

tk.Label(tolerance_frame, text="Set Tolerance", font=("Arial", 12)).pack()
tolerance_label = tk.Label(tolerance_frame, text=f"Current Tolerance: {current_tolerance}")
tolerance_label.pack()

tolerance_input = tk.Entry(tolerance_frame)
tolerance_input.pack()

tk.Button(tolerance_frame, text="Submit", command=lambda: update_tolerance()).pack()

# Function to activate system
def activate_system():
    global current_status, ignore_threshold
    current_status = "System Active"
    update_labels()
    ignore_threshold = True
    root.after(10000, reset_ignore_threshold)  # Use Tkinter instead of threading.Timer

# Function to deactivate system
def deactivate_system():
    global current_status, last_shutoff_date
    current_status = "Deactivated"
    last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_labels()

# Function to reset ignore threshold
def reset_ignore_threshold():
    global ignore_threshold
    ignore_threshold = False

# Function to update tolerance
def update_tolerance():
    global current_tolerance
    try:
        current_tolerance = float(tolerance_input.get())
        tolerance_label.config(text=f"Current Tolerance: {current_tolerance}")
        messagebox.showinfo("Success", "Tolerance updated successfully!")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid float value")

# Graph Display
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Start monitoring sensors
monitor_sensor_values()

# Run the Tkinter loop
root.mainloop()

# Cleanup GPIO when the script exits
GPIO.cleanup()
