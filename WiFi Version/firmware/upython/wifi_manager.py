# -----------------------------------------------------------------------------------------------
import network
import ujson
import socket
import machine
from time import sleep, time
from machine import Pin
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
DEBUG_WIFI = True
# -----------------------------------------------------------------------------------------------
STATUS_LED_PIN = 15
status_led_pin = Pin(STATUS_LED_PIN, Pin.OUT, value=1)  # Initially LED is OFF as Connected to GND
# status_led_pin.on()  # LED OFF
# status_led_pin.value(1)   # Also can use this format
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def flash_light_signal(count):
    try:
        # if count = 5 Loop will be: 0,1,2,3,4
        for i in range(count):
            # status_led_pin.off  # LED ON, VCC Connected
            status_led_pin.value(0)  # LED ON, VCC Connected
            sleep(0.25)
            # status_led.on         # LED OFF, VCC Connected
            status_led_pin.value(1)  # LED OFF, VCC Connected
            sleep(0.25)
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
def scan_networks():
    try:
        if DEBUG_WIFI:
            print("Scanning for WiFi Networks...")
        # -----------------------------------------------------------------------------------------------
        wlan_scan = network.WLAN(network.STA_IF)  # Create station interface
        wlan_scan.active(True)
        sleep(3)
        nets = wlan_scan.scan()
        sleep(3)
        ssids = []
        # -----------------------------------------------------------------------------------------------
        if DEBUG_WIFI:
            print("nets:", nets)

        for net in nets:
            ssid = net[0].decode('utf-8')

            if ssid and ssid not in ssids:
                ssids.append(ssid)

        if DEBUG_WIFI:
            print("Found networks:", ssids)

        return ssids
    except Exception as e:
        if DEBUG_WIFI:
            print('e:scan_networks:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def start_ap():
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid="Rokkhi-Config", authmode=network.AUTH_WPA_WPA2_PSK, password="42316237")
        status_led_pin.value(0)     # STATUS LED ON
        # -----------------------------------------------------------------------------------------------
        if DEBUG_WIFI:
            print("Rokkhi-Config AP Started!\nConnect to:", ap.ifconfig())
        # -----------------------------------------------------------------------------------------------
        return ap
    except Exception as e:
        if DEBUG_WIFI:
            print('e:start_ap:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def save_config(ssid, password):
    try:
        with open("config.json", "w") as f:
            ujson.dump({"ssid": ssid, "password": password}, f)
    except Exception as e:
        if DEBUG_WIFI:
            print('e:save_config:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def url_decode(s):
    try:
        """Decode URL-encoded string, keep + as literal if %2B"""
        if not s:
            return ""

        res = ""
        i = 0

        while i < len(s):
            if s[i] == "%" and i + 2 < len(s):
                try:
                    res += chr(int(s[i + 1:i + 3], 16))
                    i += 3
                    continue
                except:
                    pass
            elif s[i] == "+":
                res += " "  # + represents space in URL form
            else:
                res += s[i]
            i += 1

        return res.strip()
    except Exception as e:
        if DEBUG_WIFI:
            print('e:url_decode:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def start_web_server(ssid_list):
    try:
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        # -----------------------------------------------------------------------------------------------
        if DEBUG_WIFI:
            print("Web Server Started on http://192.168.4.1")
        # -----------------------------------------------------------------------------------------------
        while True:
            # -----------------------------------------------------------------------------------------------
            cl, addr = s.accept()

            if DEBUG_WIFI:
                print('Client Connected from', addr)

            try:
                # Waiting here to receive request data
                request = cl.recv(1024).decode()

                if DEBUG_WIFI:
                    print("Request:", request)
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                if DEBUG_WIFI:
                    print("e:start_web_server:1:", e)

                cl.close()
                continue
            # -----------------------------------------------------------------------------------------------

            # -----------------------------------------------------------------------------------------------
            if "/save?" in request:
                try:
                    query = request.split("GET /save?")[1].split(" ")[0]
                    params = dict(q.split("=", 1) for q in query.split("&"))

                    ssid = url_decode(params.get("ssid", ""))
                    password = url_decode(params.get("password", ""))

                    if ssid and password:
                        save_config(ssid, password)
                        # -----------------------------------------------------------------------------------------------
                        f = open('success_page.txt', 'r')
                        response = f.read()
                        f.close()
                        f = ''
                        # -----------------------------------------------------------------------------------------------
                        cl.send(response)
                        cl.close()
                        sleep(3)
                        machine.reset()
                # -----------------------------------------------------------------------------------------------
                except Exception as e:
                    if DEBUG_WIFI:
                        print("e:start_web_server:2:", e)
            # -----------------------------------------------------------------------------------------------
            else:
                # Generate SSID dropdown list
                # options = "".join([f"<option value='{s}'>{s}</option>" for s in ssid_list])
                # Generate SSID list as plain text
                # options = "<ul>" + "".join([f"<li>{s}</li>" for s in ssid_list]) + "</ul>"
                # Generate SSID list as numbered list
                options = "<ol>" + "".join([f"<li>{s}</li>" for s in ssid_list]) + "</ol>"
                # -----------------------------------------------------------------------------------------------
                f = open('index_page_part_1.txt', 'r')
                response_p1 = f.read()
                f.close()
                f = ''
                # -----------------------------------------------------------------------------------------------
                f = open('index_page_part_2.txt', 'r')
                response_p2 = f.read()
                f.close()
                f = ''
                # -----------------------------------------------------------------------------------------------
                response = response_p1 + options + response_p2
                # -----------------------------------------------------------------------------------------------
                cl.send(response)
                cl.close()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_WIFI:
            print('e:start_web_server:', e)

        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def connect_to_wifi(wifi_ssid, wifi_pass, time_out):
    try:
        # -----------------------------------------------------------------------------------------------
        wifi_connect_flag = True
        wlan = ''
        # -----------------------------------------------------------------------------------------------
        if wifi_ssid and wifi_pass:
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

                    sleep(1)
                    # -----------------------------------------------------------------------------------------------
                    if time() - start > time_out:
                        if DEBUG_WIFI:
                            print("FAILED to Connect WiFi in ", time_out, "Sec\nStarting AP Mode...")

                        wifi_connect_flag = False
                        break
        # -----------------------------------------------------------------------------------------------
        if (not wifi_ssid) or (not wifi_pass) or (not wifi_connect_flag):
            if DEBUG_WIFI:
                print("No 'SSID-Password' found! OR Somehow Failed to Connect to WiFi\nStarting AP Mode...")

            reset_wifi(3)
            # Scan available SSIDs in STA mode
            ssid_list = scan_networks()
            reset_wifi(3)
            start_ap()
            sleep(1)
            start_web_server(ssid_list)  # Serve list to page
            sleep(1)
        # -----------------------------------------------------------------------------------------------
        if wlan.isconnected():
            if DEBUG_WIFI:
                print("Connected to WiFi Successful:)")
                # print('network config:', wlan.ifconfig())
                print('IP:', wlan.ifconfig()[0])
                print('Netmask:', wlan.ifconfig()[1])
                print('Gateway:', wlan.ifconfig()[2])
                print('DNS:', wlan.ifconfig()[3])
            # -----------------------------------------------------------------------------------------------
            return True
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_WIFI:
            print('e:connect_wifi:', e)

        machine.reset()
# ***********************************************************************************************
