import time
import spidev
import RPi.GPIO as GPIO

# Raspberry Pi SPI & GPIO Setup
SYNC_PIN = 10  # CE0 (Chip Enable)
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
GPIO.output(SYNC_PIN, GPIO.HIGH)  # Ensure SYNC starts high

# AD5592R Register Addresses
REG_ADDR = {
    "NOP": 0x0,
    "SW_RESET": 0xF,
    "ADC_CONFIG": 0x4,
    "GPIO_CONFIG": 0x8,
    "GEN_CTRL_REG": 0x3,
    "ADC_SEQ": 0x2
}

def send_spi_command(command, description):
    """ Sends SPI command to AD5592R """
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001)
    spi.xfer2([(command >> 8) & 0xFF, command & 0xFF])
    GPIO.output(SYNC_PIN, GPIO.HIGH)
    time.sleep(0.000001)
    print(f"Sent: {description} (0x{command:04X})")

def read_adc_channel():
    """ Reads ADC output from AD5592R """
    GPIO.output(SYNC_PIN, GPIO.LOW)
    time.sleep(0.000001)
    received_bytes = spi.xfer2([0x00, 0x00])
    GPIO.output(SYNC_PIN, GPIO.HIGH)
    
    received_word = (received_bytes[0] << 8) | received_bytes[1]
    adc_channel = (received_word >> 12) & 0x07  # Bits [14:12] contain the ADC channel number
    adc_value = received_word & 0xFFF  # Bits [11:0] contain ADC result (12-bit data)
    
    return adc_channel, adc_value

# === AD5592R Configuration ===
print("\nConfiguring AD5592R as ADC on I/O0 & I/O1...")

# 1. Software Reset (Recommended)
send_spi_command((0 << 15) | (REG_ADDR["SW_RESET"] << 11) | 0x5AC, "Software Reset")
time.sleep(0.00025)

# 2. Configure I/O0 & I/O1 as ADC Inputs
adc_config_command = (0 << 15) | (REG_ADDR["ADC_CONFIG"] << 11) | 0x03  # ADC I/O0 & I/O1
send_spi_command(adc_config_command, "Enable ADC I/O0 & I/O1")
time.sleep(0.0005)

# 3. Set ADC Range to 0V to VREF
gen_ctrl_command = (0 << 15) | (REG_ADDR["GEN_CTRL_REG"] << 11) | 0x00  # Set range
send_spi_command(gen_ctrl_command, "Set ADC range to 0V - VREF")

# 4. Configure ADC Sequence for I/O0 & I/O1
adc_sequence_command = (0 << 15) | (REG_ADDR["ADC_SEQ"] << 11) | 0x03  # Include ADC0 & ADC1
send_spi_command(adc_sequence_command, "Set ADC sequence for I/O0 & I/O1")
time.sleep(0.0005)

print("\nAD5592R Configuration Complete. Starting ADC Read Loop...\n")

# === Continuous ADC Read Loop ===
while True:
    # Read ADC0 (First sensor)
    send_spi_command((0 << 15) | (REG_ADDR["NOP"] << 11), "Trigger ADC0 Conversion")
    time.sleep(0.005)
    channel, adc_value_0 = read_adc_channel()
    print(f"ADC{channel} Output: {adc_value_0}")

    # Read ADC1 (Second sensor)
    send_spi_command((0 << 15) | (REG_ADDR["NOP"] << 11), "Trigger ADC1 Conversion")
    time.sleep(0.005)
    channel, adc_value_1 = read_adc_channel()
    print(f"ADC{channel} Output: {adc_value_1}")

    time.sleep(1)  # Wait 1 second before next read
