import requests
import serial
import time
from time import sleep


def send_at_command(command, delay=1):
    ser.write((command + "\r\n").encode())  # Send command
    time.sleep(delay)  # Wait for response
    response = ser.read_all().decode(errors='ignore')  # Read response
    print(response)  # Print the response



server_url_get_pending = "https://rokkhi.banglasolutions.com/get_motion_call_and_sms_nos"
server_url_reset_pending = "https://rokkhi.banglasolutions.com/reset_motion_call_pending_status"



while True:
    try:
        response = requests.get(server_url_get_pending)

        if response.status_code == 200:
            data = response.json()  # Convert response to Python dictionary
            # print("Received Data:", data)

            # Extract "call_info" list
            call_info_list = data.get("call_info", [])

            # Create a list of formatted "device_info_id, called_to" values
            formatted_data = [f"{item['device_info_id']}, {item['called_to']}" for item in call_info_list]

            # Join the list into a single comma-separated string
            result = ", ".join(formatted_data)

            # print("Formatted Output:", result)


            comma_string = result
            data_list = [item.strip() for item in comma_string.split(",")]

            # print(data_list)


            # Replace 'COM3' with your actual port (e.g., '/dev/ttyUSB0' for Linux)
            ser = serial.Serial(port='COM7', baudrate=9600, timeout=1)

            # Initialize the modem
            send_at_command("AT")  # Check communication
            send_at_command("AT+CSQ")  # Check signal strength
            send_at_command("AT+CCID")  # Get SIM card info
            
            for item in data_list:
                if item != '1' and item != '2':
                    print('item>>>>', item)
                    # Call from Modem Here
                    if item:
                        print('---------')
                        send_at_command("ATD" + item + ";")  # Dial a number (Change to your number)
                        sleep(20)
                        send_at_command("ATH")  # Get SIM card info
                        sleep(5)
                    

            ser.close()  # Close the serial connection


            response = requests.get(server_url_reset_pending)

            if response.status_code == 200:
                data = response.json()  # Convert response to Python dictionary
                print("Received Data:", data)


            print("DONE")

        else:
            print("Failed to fetch data, Status Code:", response.status_code)

        sleep(5)
    except Exception as e:
        print('e: ', e)
