# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 11:37:32 2025

@author: Zakary.Gruber
"""

import time
import spidev
import RPi.GPIO as GPIO

SYNC_PIN = 10
SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 1000000  # 1 MHz

# Initialize SPI
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = SPI_SPEED_HZ
spi.mode = 0b00

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SYNC_PIN, GPIO.OUT)
GPIO.output(SYNC_PIN, GPIO.HIGH)

REG_ADDR = {"NOP": 0x0, "ADC_SEQ": 0x2}

def send_spi_command(command):
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001)
    spi.xfer2([(command >> 8) & 0xFF, command & 0xFF])
    GPIO.output(SYNC_PIN, GPIO.HIGH)
    time.sleep(0.000001)

def read_adc_channel():
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001)
    received_bytes = spi.xfer2([0x00, 0x00])
    GPIO.output(SYNC_PIN, GPIO.HIGH)
    
    received_word = (received_bytes[0] << 8) | received_bytes[1]
    return received_word & 0xFFF  # Extract ADC data (12 bits)

# Start ADC read loop
print("Reading ADC values every second...")
while True:
    send_spi_command((0 << 15) | (REG_ADDR["NOP"] << 11))  # Trigger ADC conversion
    time.sleep(0.002)  # Allow ADC conversion time
    adc_value = read_adc_channel()
    print(f"ADC Output: {adc_value}")
    time.sleep(1)  # Wait 1 second before the next read
