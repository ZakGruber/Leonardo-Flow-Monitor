# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 12:12:11 2025

@author: Zakary.Gruber
"""

import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
SENSOR1_PIN = 17
SENSOR2_PIN = 18
SOLENOID_PIN = 27


# Activate GPIO pins
GPIO.setup(SENSOR1_PIN, GPIO.IN)
GPIO.setup(SENSOR2_PIN, GPIO.IN)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)

PULSES_PER_GALLON = 2840

flow_count1 = 0
flow_count2 = 0
start_time = None
sleep_time = .02

# Functions to recieve a signal from the flow monitors
def pulse_detected1(channel):
    global flow_count1
    flow_count1 += 1

def pulse_detected2(channel):
    global flow_count2
    flow_count2 += 1

GPIO.add_event_detect(SENSOR1_PIN, GPIO.RISING, callback=pulse_detected1)
GPIO.add_event_detect(SENSOR2_PIN, GPIO.RISING, callback=pulse_detected2)

flow_rate_1 = []
flow_rate_2 = []
for i in range(0, 50):
    rate1 = flow_count1 / PULSES_PER_GALLON
    rate2 = flow_count2 / PULSES_PER_GALLON
    flow_count1 = 0
    flow_count2 = 0
    flow_rate_1.append(rate1)
    flow_rate_2.append(rate2)
    time.sleep(sleep_time)
    
for n in range(len(flow_rate_1)):
    print(f"rate 1: {flow_rate_1[n]}")
    print(f"rate 2: {flow_rate_2[n]}")
    
# Create time axis based on number of samples and sleep_time
time_axis = [n * sleep_time for n in range(len(flow_rate_1))]

# Plot flow_rate_1
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_axis, flow_rate_1, marker='o', color='blue', label='Flow Rate 1')
plt.title('Flow Rate 1 over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Flow Rate (gallons/sec)')
plt.grid(True)
plt.legend()

# Plot flow_rate_2
plt.subplot(2, 1, 2)
plt.plot(time_axis, flow_rate_2, marker='o', color='green', label='Flow Rate 2')
plt.title('Flow Rate 2 over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Flow Rate (gallons/sec)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
