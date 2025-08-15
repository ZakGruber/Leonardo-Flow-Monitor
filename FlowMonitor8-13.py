#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 2 2025

@author: Zakary.Gruber
"""
import RPi.GPIO as GPIO
import tkinter as tk
import tkinter.simpledialog as sd
from tkinter import messagebox
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import signal

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
SENSOR1_PIN = 17
SENSOR2_PIN = 18
SOLENOID_PIN = 27

def graceful_exit(signum, frame):
    GPIO.output(SOLENOID_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.cleanup()
    sys.exit(0)

# Activate GPIO pins
GPIO.setup(SENSOR1_PIN, GPIO.IN)
GPIO.setup(SENSOR2_PIN, GPIO.IN)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

PULSES_PER_GALLON = 2840

# Global Variables
current_password = "admin123"
ignore_threshold = False
last_shutoff_date = "No shutoff recorded"
current_status = "Inactive"
current_tolerance = 0
system_name = "Flow Monitor 1"
duration_threshold = 10

# Active variables
sensor_differences = []
time_stamps = []
flow_count1 = 0
flow_count2 = 0
start_time = None


# Functions to recieve a signal from the flow monitors
def pulse_detected1(channel):
    global flow_count1
    flow_count1 += 1

def pulse_detected2(channel):
    global flow_count2
    flow_count2 += 1

GPIO.add_event_detect(SENSOR1_PIN, GPIO.RISING, callback=pulse_detected1)
GPIO.add_event_detect(SENSOR2_PIN, GPIO.RISING, callback=pulse_detected2)

# Automatic functions
def update_labels():
    status_label.config(text=f"Current cooling state: {current_status}")
    shutoff_label.config(text=f"Last shutoff logged at: {last_shutoff_date}")
    current_tolerance_label.config(text=f"Current accepted flow difference: {current_tolerance} (gal)")
    activation_delay_label.config(text=f"Current activation delay: {duration_threshold} (sec)")

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

        if len(sensor_differences) > 100:
            sensor_differences.pop(0)
            time_stamps.pop(0)

    if difference > abs(current_tolerance):
        if start_time is None:
            start_time = time.time()
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration_threshold:
            GPIO.output(SOLENOID_PIN, GPIO.HIGH)
            last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_status = "Inactive"
            update_labels()
            start_time = None
    else:
        start_time = None

    root.after(1000, update_graph)

def update_graph():
    global time_stamps, sensor_differences

    if time_stamps and sensor_differences and len(time_stamps) == len(sensor_differences):
        normalized_t = [t - time_stamps[0] for t in time_stamps]
        ax.clear()
        ax.plot(normalized_t, sensor_differences, label="Flow Rate Difference (gal/s)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amount (gallons)")
        ax.set_ylim(bottom=0)
        ax.legend()
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

    root.after(1000, monitor_sensor_values)

# GUI
# Main window
root = tk.Tk()
root.title("Water Flow Monitor")
root.geometry("600x650")

info_label = tk.Label(root, text=system_name, font=("Arial", 14, "bold"))
info_label.pack()

status_label = tk.Label(root, text=f"Current cooling state: {current_status}", font=("Arial",20))
status_label.pack()

shutoff_label = tk.Label(root, text=f"Last shutoff logged at: {last_shutoff_date}")
shutoff_label.pack()

current_tolerance_label = tk.Label(root, text=f"Current accepted flow difference: {current_tolerance} (gal)")
current_tolerance_label.pack()

activation_delay_label = tk.Label(root, text=f"Current activation delay: {duration_threshold} (sec)")
activation_delay_label.pack()

# Admin Password Entry
pw_frame = tk.Frame(root)
pw_frame.pack(pady=10)

tk.Label(pw_frame, text="Enter Admin Password", font=("Arial", 12)).pack()
pw_entry = tk.Entry(pw_frame, show="*")
pw_entry.pack()

def check_password():
    if pw_entry.get() == current_password:
        pw_entry.delete(0, tk.END)
        show_admin_panel()
    else:
        messagebox.showerror("Access Denied", "Incorrect password.")

tk.Button(pw_frame, text="Enter", command=check_password).pack(pady=5)

# Open solenoid to send monitored cooling
def activate_system():
    global current_status, ignore_threshold
    GPIO.output(SOLENOID_PIN, GPIO.LOW)
    current_status = "Active"
    update_labels()
    ignore_threshold = True
    root.after(10000, reset_ignore_threshold)

# Close solenoid, no more monitored cooling
def deactivate_system():
    global current_status, last_shutoff_date
    GPIO.output(SOLENOID_PIN, GPIO.HIGH)
    current_status = "Inactive"
    last_shutoff_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_labels()

def reset_ignore_threshold():
    global ignore_threshold
    ignore_threshold = False

# Password protected admin control panel
def show_admin_panel():
    admin_win = tk.Toplevel(root)
    admin_win.title("Admin Panel")
    admin_win.geometry("350x280")
    admin_win.transient(root)
    admin_win.grab_set()
    admin_win.focus_force()
    admin_win.lift()


    tk.Label(admin_win, text= f"Current password:").pack(pady=(10, 0))
    pwd_entry = tk.Entry(admin_win, show="*")
    pwd_entry.insert(0, current_password)
    pwd_entry.pack()

    tk.Label(admin_win, text="System name:").pack(pady=(10, 0))
    name_entry = tk.Entry(admin_win)
    name_entry.insert(0, system_name)
    name_entry.pack()

    tk.Label(admin_win, text="Acceptable flow difference:").pack(pady=(10, 0))
    tol_entry = tk.Entry(admin_win)
    tol_entry.insert(0, str(current_tolerance))
    tol_entry.pack()

    tk.Label(admin_win, text="Activation Delay (sec):").pack(pady=(10, 0))
    dur_entry = tk.Entry(admin_win)
    dur_entry.insert(0, str(duration_threshold))
    dur_entry.pack()

    def save_admin_settings():
        global current_password, system_name, current_tolerance, duration_threshold
        current_password = pwd_entry.get()
        system_name = name_entry.get()
        try:
            current_tolerance = float(tol_entry.get())
            duration_threshold = float(dur_entry.get())
            update_labels()
        except ValueError:
            messagebox.showerror("Error", "Acceptable flow difference and duration must be numbers")
            return

        info_label.config(text=system_name)
        messagebox.showinfo("Admin", "Settings saved.")
        admin_win.destroy()

    tk.Button(admin_win, text="Confirm changes", command=save_admin_settings).pack(pady=15)

# Manual shutoff switch
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Label(control_frame, text="ON/OFF", font=("Arial", 12)).pack()
tk.Button(control_frame, text="ON", command=activate_system).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="OFF", command=deactivate_system).pack(side=tk.LEFT, padx=5)

# Graph
fig, ax = plt.subplots(figsize=(6, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

monitor_sensor_values()

try:
    root.mainloop()
finally:
    GPIO.output(SOLENOID_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.cleanup()
