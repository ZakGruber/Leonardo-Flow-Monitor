import spidev
import time

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device CE0
spi.max_speed_hz = 500000  # Adjust as needed

# ADC resolution and reference voltage
ADC_RESOLUTION = 4096  # 12-bit ADC (2^12)
REF_VOLTAGE = 3.3  # Assuming 3.3V reference voltage

# 4-20mA conversion
MIN_CURRENT = 4.0  # mA
MAX_CURRENT = 20.0  # mA

def read_adc(channel):
    """Reads ADC value from given channel."""
    if channel not in [0, 1]:  # Assuming channels 0 & 1 are used
        raise ValueError("Invalid channel. Must be 0 or 1.")

    # Build command: Start bit (1), Single-ended (1), Channel select
    command = [0x01, (channel << 4) | 0x80, 0x00]
    response = spi.xfer2(command)
    
    # Extract the 12-bit result from the response
    raw_adc = ((response[1] & 0x0F) << 8) | response[2]
    
    return raw_adc

def convert_to_mA(adc_value):
    """Converts ADC reading to 4-20 mA range."""
    voltage = (adc_value / ADC_RESOLUTION) * REF_VOLTAGE
    current = (voltage / REF_VOLTAGE) * (MAX_CURRENT - MIN_CURRENT) + MIN_CURRENT
    return round(current, 2)

try:
    while True:
        adc_0 = read_adc(0)
        adc_1 = read_adc(1)
        current_0 = convert_to_mA(adc_0)
        current_1 = convert_to_mA(adc_1)

        print(f"ADC 0: {adc_0} -> {current_0} mA")
        print(f"ADC 1: {adc_1} -> {current_1} mA")

        time.sleep(1)  # Read every second

except KeyboardInterrupt:
    spi.close()
    print("Exiting...")
