
import serial
import time

# Replace 'COM3' with your actual port (e.g., '/dev/ttyUSB0' for Linux)
ser = serial.Serial(port='COM7', baudrate=9600, timeout=1)

def send_at_command(command, delay=1):
    ser.write((command + "\r\n").encode())  # Send command
    time.sleep(delay)  # Wait for response
    response = ser.read_all().decode(errors='ignore')  # Read response
    print(response)  # Print the response


# Initialize the modem
send_at_command("AT")  # Check communication
send_at_command("AT+CSQ")  # Check signal strength
send_at_command("AT+CCID")  # Get SIM card info
send_at_command("ATD+8801618354444;")  # Dial a number (Change to your number)

ser.close()  # Close the serial connection










