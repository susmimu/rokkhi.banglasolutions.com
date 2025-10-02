# -----------------------------------------------------------------------------------------------
import network
import ujson
import machine
from time import sleep, time
from machine import Pin
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
DEBUG_WIFI = True
# -----------------------------------------------------------------------------------------------
STATUS_LED_PIN = 2
status_led_pin = Pin(STATUS_LED_PIN, Pin.OUT, value=0)  # Initially LED is OFF
# status_led_pin.on()  # LED OFF
# status_led_pin.value(1)   # Also can use this format
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def flash_light_signal(count):
    try:
        if DEBUG_WIFI:
            print(f"LED Flash for {count} Times!")
        # -----------------------------------------------------------------------------------------------
        # if count = 5 Loop will be: 0,1,2,3,4
        for i in range(count):
            # status_led_pin.off  # LED ON, VCC Connected
            status_led_pin.value(1)  # LED ON, VCC Connected
            sleep(0.25)
            # status_led.on         # LED OFF, VCC Connected
            status_led_pin.value(0)  # LED OFF, VCC Connected
            sleep(0.75)
    except Exception as e:
        if DEBUG_WIFI:
            print('e:flash_light_signal():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def reset_wifi(delay_sec):
    try:
        # -----------------------------------------------------------------------------------------------
        wlan_rst = network.WLAN()  # create station interface (the default, see below for an access point interface)
        # Turn Wi-Fi OFF
        wlan_rst.active(False)
        sleep(delay_sec)

        if DEBUG_WIFI:
            print("Wi-Fi reset...")
    except Exception as e:
        if DEBUG_WIFI:
            print('e:reset_wifi:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def connect_to_wifi(wifi_ssid, wifi_pass, time_out):
    try:
        # -----------------------------------------------------------------------------------------------
        wlan = network.WLAN()  # create station interface (the default, see below for an access point interface)
        wlan.active(True)  # activate the interface
        sleep(1)
        # -----------------------------------------------------------------------------------------------
        # Check if the station is connected to an AP
        if not wlan.isconnected():
            if DEBUG_WIFI:
                print("NOT Connected to WiFi")

            wlan.connect(wifi_ssid, wifi_pass)  # Connect to an AP
            # -----------------------------------------------------------------------------------------------
            start = time()
            # Waiting Until Connect
            while not wlan.isconnected():
                if DEBUG_WIFI:
                    print("Trying to connect WiFi...")

                flash_light_signal(1)
                # -----------------------------------------------------------------------------------------------
                if time() - start > time_out:
                    if DEBUG_WIFI:
                        print("FAILED to Connect WiFi in ", time_out, "Sec\nRebooting...")

                    machine.reset()
        # -----------------------------------------------------------------------------------------------
        if wlan.isconnected():
            if DEBUG_WIFI:
                print("-----------------------------------------------------------------------")
                print("Connected to WiFi Successful:)")
                # print('network config:', wlan.ifconfig())
                print('IP:', wlan.ifconfig()[0])
                print('Netmask:', wlan.ifconfig()[1])
                print('Gateway:', wlan.ifconfig()[2])
                print('DNS:', wlan.ifconfig()[3])
                print("-----------------------------------------------------------------------")
            # -----------------------------------------------------------------------------------------------
            sleep(3)
            flash_light_signal(2)
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_WIFI:
            print('e:connect_wifi:', e)

        machine.reset()
# ***********************************************************************************************
