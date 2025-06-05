# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 10:21:41 2025

@author: Zakary.Gruber
"""

import spidev # Re-added: Needed for SPI communication
import RPi.GPIO as GPIO
import time

SYNC_PIN = 10 # Example: GPIO8 (CE0 on SPI0 header)


SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 1000000 # 1 MHz (1,000,000 Hz) - safe for both read/write

# Initialize SPI device
spi = spidev.SpiDev() # Re-added: SPI device initialization

# --- Global Variables / Chip State Tracking ---
# These flags help ensure operations are performed only after configuration
adc_configured = False
gpio_configured = False

# --- Helper Functions ---

def log_message(message, message_type='info'):
    """
    Prints messages to the console with color coding.
    """
    color_map = {
        'info': '\033[90m',    # Grey
        'command': '\033[92m', # Green
        'result': '\033[94m',  # Blue
        'warning': '\033[93m', # Yellow
        'error': '\033[91m',   # Red
        'reset': '\033[0m'     # Reset color
    }
    print(f"{color_map.get(message_type, color_map['reset'])}{message}{color_map['reset']}")

def send_spi_command(command, description):
    """
    Sends a 16-bit command to the AD5592R via SPI.
    The command is split into two 8-bit bytes (MSB first).
    """
    # Pull SYNC low to start communication
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001) # Small delay for SYNC to settle (microseconds)

    # Split 16-bit command into two 8-bit bytes (MSB first)
    byte1 = (command >> 8) & 0xFF
    byte0 = command & 0xFF

    log_message(f"Sending SPI Command: 0x{command:04X} ({command:016b}) - {description}", 'command')
    try:
        # Transfer the two bytes
        spi.xfer2([byte1, byte0])
    except Exception as e:
        log_message(f"SPI transfer error: {e}", 'error')
    finally:
        # Pull SYNC high to end communication
        GPIO.output(SYNC_PIN, GPIO.HIGH)
        time.sleep(0.000001) # Small delay after SYNC goes high

def read_spi_data(description, num_bytes=2):
    """
    Reads data from the AD5592R via SPI.
    Sends dummy bytes to clock out data.
    """
    # Pull SYNC low to start communication
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001) # Small delay for SYNC to settle

    try:
        # Send dummy bytes to clock out 16 bits (2 bytes)
        # The AD5592R clocks out data on the rising edge of SCLK
        # while SYNC is low.
        received_bytes = spi.xfer2([0x00] * num_bytes) # Send dummy bytes
        
        # Combine bytes into a 16-bit word
        received_word = (received_bytes[0] << 8) | received_bytes[1]
        log_message(f"Received SPI Data: 0x{received_word:04X} ({received_word:016b}) - {description}", 'result')
        return received_word
    except Exception as e:
        log_message(f"SPI read error: {e}", 'error')
        return None
    finally:
        # Pull SYNC high to end communication
        GPIO.output(SYNC_PIN, GPIO.HIGH)
        time.sleep(0.000001) # Small delay after SYNC goes high



REG_ADDR = {
    "NOP": 0x0, # NOP register is used here to clock out ADC results
    "SW_RESET": 0xF,
    "ADC_CONFIG": 0x4,
    "GPIO_CONFIG": 0x8,  # GPIO Write Configuration Register
    "GEN_CTRL_REG": 0x3,
    "ADC_SEQ": 0x2,
    "GPIO_OUTPUT": 0x9,  # GPIO Write Data Register
}

# --- AD5592R Configuration Functions ---

def configure_ad5592r_minimal():
    """
    Configures I/O0 as ADC input, I/O2 as GPIO output.
    Configures I/O1 as ADC input, I/O3 as GPIO output.
    Sets ADC range to 0V to VREF.
    """
    global adc_configured, gpio_configured
    log_message("\n--- Starting AD5592R Minimal Configuration ---", 'info')

    # 1. Reset the chip (optional, but good practice)
    # Command: MSB=0 (0), REG_ADDR=0xF (SW_RESET), DATA=0x5AC
    send_spi_command((0 << 15) | (REG_ADDR["SW_RESET"] << 11) | 0x5AC, "Software Reset AD5592R")
    time.sleep(0.00025) # Wait for reset to complete (250 us max)

    # 2. Configure I/O0 and I/O1 as ADC inputs (ADC_CONFIG Register - 0x4)
    # Bits[7:0] for I/O7 to I/O0. Set I/O0 (Bit 0) and I/O1 (Bit 1) to 1.
    # Value: 0b00000011 (0x03)
    adc_config_data = 0x03 # I/O0 and I/O1
    adc_config_command = (0 << 15) | (REG_ADDR["ADC_CONFIG"] << 11) | adc_config_data
    send_spi_command(adc_config_command, "Configure I/O0, I/O1 as ADC Inputs")
    adc_configured = True


    gpio_config_data = 0x0C # I/O2 and I/O3
    gpio_config_command = (0 << 15) | (REG_ADDR["GPIO_CONFIG"] << 11) | gpio_config_data
    send_spi_command(gpio_config_command, "Configure I/O2, I/O3 as GPIO Outputs")
    gpio_configured = True

    # 4. Set ADC Range to 0V to VREF (GEN_CTRL_REG Register - 0x3)
    # Bit 5 (ADC_RANGE) = 0 for 0V to VREF
    # All other bits (including DAC_RANGE) are default 0.
    gen_ctrl_data = 0x00 # All reserved bits 0, ADC_RANGE=0, DAC_RANGE=0
    gen_ctrl_command = (0 << 15) | (REG_ADDR["GEN_CTRL_REG"] << 11) | gen_ctrl_data
    send_spi_command(gen_ctrl_command, "Set ADC range to 0V to VREF")

    # 5. Configure ADC Sequence to include I/O0 and I/O1 (ADC_SEQ Register - 0x2)
    # Bits[7:0] for ADC7 to ADC0. Set ADC0 (Bit 0) and ADC1 (Bit 1) to 1.
    # Value: 0b00000011 (0x03)
    # Bit 9 (REP) = 0 (No repetition for this example)
    # Bit 8 (TEMP) = 0 (No temperature indicator for this example)
    adc_sequence_data = 0x03
    adc_sequence_command = (0 << 15) | (REG_ADDR["ADC_SEQ"] << 11) | adc_sequence_data
    send_spi_command(adc_sequence_command, "Set ADC sequence for I/O0 and I/O1")
    time.sleep(0.0005) # Allow ADC to track input (500 ns min, add margin)

    log_message("--- AD5592R Minimal Configuration Complete ---", 'info')

def set_digital_outputs(io2_val, io3_val):
    """
    Sets the state of the digital outputs I/O2 and I/O3.
    """
    if not gpio_configured:
        log_message("GPIOs not configured. Please run 'configure_ad5592r_minimal()' first.", 'warning')
        return

    # GPIO Write Data Register (0x9)
    # Bits[7:0] correspond to I/O7 to I/O0.
    # We want to set I/O2 (Bit 2) and I/O3 (Bit 3).
    gpio_data = 0
    if io2_val == 1:
        gpio_data |= (1 << 2) # Set I/O2 high
    if io3_val == 1:
        gpio_data |= (1 << 3) # Set I/O3 high

    gpio_output_command = (0 << 15) | (REG_ADDR["GPIO_OUTPUT"] << 11) | gpio_data
    send_spi_command(gpio_output_command, f"Set I/O2 to {io2_val} and I/O3 to {io3_val}")
    log_message(f"Digital outputs I/O2: {io2_val}, I/O3: {io3_val}", 'info')

def read_adc_channel(adc_address):
    """
    Initiates a conversion and reads the result for a single ADC channel.
    Note: The AD5592R clocks out the *previous* conversion result.
    To get a fresh reading for a specific channel, you typically:
    1. Send a command that initiates conversion (e.g., a dummy write, or the ADC_SEQ command).
    2. Then, send another command (e.g., NOP or another ADC_SEQ command) to clock out the result.
    """
    if not adc_configured:
        log_message("ADCs not configured. Please run 'configure_ad5592r_minimal()' first.", 'warning')
        return None

    log_message(f"Initiating conversion and reading result for ADC{adc_address}...", 'info')

    # Step 1: Initiate conversion for the desired channel.
    # The ADC_SEQ register was set to include I/O0 and I/O1.
    # A SYNC falling edge initiates conversion on the *next* channel in the sequence.
    # We send a NOP command to clock out the previous result (if any) and trigger next conversion
    send_spi_command((0 << 15) | (REG_ADDR["NOP"] << 11) | 0x00, f"NOP (to clock out previous result for ADC{adc_address})")
    time.sleep(0.000002) # Conversion time is 2 us, wait for it to complete

    # Step 2: Read the ADC result.
    # The AD5592R will output the result of the conversion that just completed.
    # We send another NOP to clock out the data.
    # The data format is: Bit 15 = 0, Bits[14:12] = ADC Address, Bits[11:0] = ADC Data
    received_word = read_spi_data(f"ADC{adc_address} Conversion Result")

    if received_word is not None:
        # Extract ADC address and data
        received_adc_address = (received_word >> 12) & 0x7 # Bits 14:12
        adc_data = received_word & 0xFFF # Bits 11:0

        # Verify the address if needed (optional)
        if received_adc_address == adc_address:
            log_message(f"ADC{received_adc_address} (I/O{received_adc_address}) Result: {adc_data} (0x{adc_data:03X})", 'info')
            return adc_data
        else:
            log_message(f"Warning: Expected ADC{adc_address}, but received result for ADC{received_adc_address}. This might indicate a sequence mismatch.", 'warning')
            log_message(f"Raw data: {adc_data} (0x{adc_data:03X})", 'info')
            return adc_data # Still return the data, but warn
    return None

# --- Main Program Flow ---
if __name__ == "__main__":
    # Configure RPi.GPIO
    GPIO.setmode(GPIO.BCM) # Use Broadcom pin-numbering scheme
    GPIO.setup(SYNC_PIN, GPIO.OUT)
    GPIO.output(SYNC_PIN, GPIO.HIGH) # Ensure SYNC is high initially

    # Open SPI bus
    try:
        spi.open(SPI_BUS, SPI_DEVICE)
        spi.max_speed_hz = SPI_SPEED_HZ
        spi.mode = 0b00 # SPI Mode 0 (CPOL=0, CPHA=0)
        log_message(f"SPI bus {SPI_BUS}, device {SPI_DEVICE} opened at {SPI_SPEED_HZ/1000000} MHz, Mode {spi.mode}", 'info')

        # Step 1: Configure the AD5592R chip with minimal settings
        configure_ad5592r_minimal()

        # Step 2: Demonstrate setting digital outputs (I/O2 and I/O3)
        log_message("\n--- Demonstrating Digital Output Control ---", 'info')
        set_digital_outputs(io2_val=1, io3_val=0) # Set I/O2 High, I/O3 Low
        time.sleep(1) # See the effect
        set_digital_outputs(io2_val=0, io3_val=1) # Set I/O2 Low, I/O3 High
        time.sleep(1) # See the effect
        set_digital_outputs(io2_val=0, io3_val=0) # Set both Low
        time.sleep(1)

        log_message("\n--- Demonstrating ADC Value Reading ---", 'info')

        # Read ADC0 (first in sequence)
        adc0_value = read_adc_channel(0)
        time.sleep(0.1) # Small delay between reads

        # Read ADC1 (second in sequence)
        adc1_value = read_adc_channel(1)
        time.sleep(0.1)

        # Read ADC0 again (sequence wraps around)
        adc0_value_new = read_adc_channel(0)
        time.sleep(0.1)

        log_message("\nDemonstration Finished.", 'info')

    except FileNotFoundError:
        log_message("SPI device not found. Ensure SPI is enabled and connected.", 'error')
        log_message("Run 'sudo raspi-config' -> Interface Options -> SPI -> Yes", 'error')
    except PermissionError:
        log_message("Permission denied. Run script with 'sudo python3 your_script_name.py'", 'error')
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}", 'error')
    finally:
        # Clean up GPIO and SPI resources
        if 'spi' in locals():
            spi.close()
            log_message("SPI bus closed.", 'info')
        GPIO.cleanup()
        log_message("GPIO cleaned up.", 'info')
