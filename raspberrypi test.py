# -*- coding: utf-8 -*-
"""
Created on Wed May 21 15:02:00 2025

@author: Zakary.Gruber
"""
from gpiozero import LED, InputDevice, Button


fm1 = InputDevice(17)
green = LED(15)
red = LED(21)
toggle = Button(13)

flow_rate_mA = (fm1.value * 20)

universe_bool = True


        
def toggle_on():
    global universe_bool
    while universe_bool == True:
        green.on()
        print(f"Current flow rate: {flow_rate_mA}mA")
        if toggle.is_active():
            universe_bool = False
            toggle_off()

def toggle_off():
    global universe_bool
    while universe_bool == False:
        red.on()
        print(f"Current flow rate: {flow_rate_mA}mA (Should be 0)")
        if toggle.is_active():
            universe_bool = True
            toggle_on()
            
toggle_on()