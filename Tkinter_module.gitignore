#For the raspberry pi without dearpygui
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 09:39:44 2025

@author: Zakary.Gruber
"""

import tkinter as tk
from tkinter import messagebox
import random as rand
import time
import datetime
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize global variables
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

# Function to simulate sensor values
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

# Function to monitor sensor values
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
                update_labels()

                start_time = None
        else:
            start_time = None

        time.sleep(0.5)

monitor_thread = threading.Thread(target=monitor_sensor_values, daemon=True)
monitor_thread.start()

# Function to reset ignore threshold
def reset_ignore_threshold():
    global ignore_threshold
    ignore_threshold = False

# Function to update labels
def update_labels():
    status_label.config(text=f"Current status: {current_status}")
    shutoff_label.config(text=f"System shutoff recorded at: {last_shutoff_date}")

# Function to activate system
def on_button_activation():
    global current_status, ignore_threshold
    current_status = "System Active"
    update_labels()

    ignore_threshold = True
    threading.Timer(10, reset_ignore_threshold).start()

# Function to deactivate system
def off_button_activation():
    global current_status, last_shutoff_date
    current_status = "Deactivated"
    last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_labels()

# Function to update tolerance
def update_tolerance():
    global current_tolerance
    try:
        current_tolerance = float(tolerance_input.get())
        tolerance_label.config(text=f"Current Tolerance: {current_tolerance}")
        messagebox.showinfo("Success", "Tolerance updated successfully!")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid float value")

# Function to update graph
def update_graph():
    if time_stamps and sensor_differences:
        min_time = min(time_stamps)
        normalized_timestamps = [t - min_time for t in time_stamps]

        ax.clear()
        ax.plot(normalized_timestamps, sensor_differences, label="Sensor Difference")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Difference (mA)")
        ax.legend()
        canvas.draw()

    # Schedule the next update (every 1 second)
    root.after(1000, update_graph)

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
tk.Button(control_frame, text="ON", command=on_button_activation).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="OFF", command=off_button_activation).pack(side=tk.RIGHT, padx=5)

# Tolerance Setting
tolerance_frame = tk.Frame(root)
tolerance_frame.pack(pady=10)

tk.Label(tolerance_frame, text="Set Tolerance", font=("Arial", 12)).pack()
tolerance_label = tk.Label(tolerance_frame, text=f"Current Tolerance: {current_tolerance}")
tolerance_label.pack()

tolerance_input = tk.Entry(tolerance_frame)
tolerance_input.pack()

tk.Button(tolerance_frame, text="Submit", command=update_tolerance).pack()

# Graph Display
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

tk.Button(root, text="Update Graph", command=update_graph).pack(pady=5)

#update graph
update_graph()

# Run the Tkinter loop
root.mainloop()
