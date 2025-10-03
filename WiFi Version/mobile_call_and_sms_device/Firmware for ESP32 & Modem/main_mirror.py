# -----------------------------------------------------------------------------------------------
from machine import Pin
import esp32
import esp
import machine
import socket
from time import sleep
from machine import RTC
import ubinascii
from machine import WDT
import gc
import ucryptolib
import network
import usocket as socket
import ustruct
import ujson

import modem_mgnt
import wifi_manager
import uart_mgnt
# -----------------------------------------------------------------------------------------------
wifi_ssid = 'ZerOneLab'
wifi_pass = 'zerone333'
# -----------------------------------------------------------------------------------------------
HOST_IP = '103.159.2.41'
HOST_DOMAIN = 'rokkhi.banglasolutions.com'
HOST_PORT = 9473
# -----------------------------------------------------------------------------------------------
dev_sock = ''
reply_buff = ''
SOCKET_TIMEOUT = 45
# -----------------------------------------------------------------------------------------------
hb_counter = 0
hb_delay = 15
# -----------------------------------------------------------------------------------------------
DEBUG = True
# -----------------------------------------------------------------------------------------------
wdt = WDT(timeout=180000)  # Enable it with a timeout of 180 seconds
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def show_hardware_info():
    try:
        # -----------------------------------------------------------------------------------------------
        mem_free = gc.mem_free()
        flash_size = esp.flash_size()
        mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
        # Read the internal temperature of the MCU, in Fahrenheit
        raw_temperature = esp32.raw_temperature()
        idf_heap_info = esp32.idf_heap_info(esp32.HEAP_DATA)
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("=============== System Information! ===============")
            print("gc.mem_free():", mem_free, "Bytes")
            print("gc.mem_free():", mem_free / 1048576, "MB")
            # Without PSRAM → around 100 KB free.
            # With PSRAM → a few MB free (e.g., 4 MB).
            print('Flash size in byte:', flash_size)
            print('MAC:', mac)
            print('raw_temperature[F]:', raw_temperature)
            print("idf_heap_info:", idf_heap_info)
            print("===================================================")
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG:
            print('e:show_hardware_info:', e)

        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def connect_to_cloud():
    try:
        global HOST_DOMAIN, HOST_PORT, dev_sock
        # -----------------------------------------------------------------------------------------------
        # Connect to TCP server
        addr = socket.getaddrinfo(HOST_DOMAIN, HOST_PORT)[0][-1]
        dev_sock = socket.socket()
        dev_sock.settimeout(SOCKET_TIMEOUT)  # wait max 10 seconds
        dev_sock.connect(addr)
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("Cloud Connection Success! Connected to:", addr)

        wifi_manager.flash_light_signal(3)
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG:
            print("Cloud Connection FAILED!\nRebooting...")
            print('e:connect_to_cloud:', e)

        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def send_flag_to_server_and_wait_for_reply(flag):
    try:
        global dev_sock, reply_buff
        # -----------------------------------------------------------------------------------------------
        # print("Sending'", flag, "'to Server and Waiting for Reply...")
        # -----------------------------------------------------------------------------------------------
        dev_sock.send(flag.encode())  # encode() → convert to bytes
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("Sent:", flag)
        # -----------------------------------------------------------------------------------------------
        # Receive response
        """
        Set timeout for 10 seconds
        🔑 Key points:
        * dev_sock.settimeout(10) → makes recv() wait 10 seconds max.
        * If no data is received in that time → raises socket.timeout.
        * After the call, you can reset the timeout back if needed: dev_sock.settimeout(None) (wait forever again).
        """
        # dev_sock.settimeout(SOCKET_TIMEOUT)
        # -----------------------------------------------------------------------------------------------
        try:
            reply_buff = dev_sock.recv(256)
            # -----------------------------------------------------------------------------------------------
            if DEBUG:
                print("Received:", reply_buff.decode())
            # -----------------------------------------------------------------------------------------------
            if flag in reply_buff.decode():
                return True
        # -----------------------------------------------------------------------------------------------
        except socket.timeout:
            if DEBUG:
                print("Timeout: No reply within", SOCKET_TIMEOUT, "seconds")
        except Exception as e:
            if DEBUG:
                print("e:flag:", e)
        # -----------------------------------------------------------------------------------------------
        return False
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG:
            print('e:send_flag_to_server_and_wait_for_reply:', e)
            print('Rebooting:', e)
        # -----------------------------------------------------------------------------------------------
        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def start_main_program():
    try:
        global hb_counter
        # -----------------------------------------------------------------------------------------------
        sleep(1) # Startup Delay
        # -----------------------------------------------------------------------------------------------
        wifi_manager.flash_light_signal(1)
        # -----------------------------------------------------------------------------------------------
        # show_hardware_info()
        # -----------------------------------------------------------------------------------------------
        wifi_manager.reset_wifi(1)
        wifi_manager.connect_to_wifi(wifi_ssid, wifi_pass, 30)
        # -----------------------------------------------------------------------------------------------
        # If WiFi Connection FAILED System will Reboot in ABOVE Line, So, Bellow code will NOT Execute
        uart_mgnt.uart2_init()
        # If UART Init FAILED System will Reboot in ABOVE Line, So, Bellow code will NOT Execute
        # -----------------------------------------------------------------------------------------------
        modem_mgnt.restart_modem()
        # -----------------------------------------------------------------------------------------------
        # Dynamic Wait for Network and GSM Ready
        if modem_mgnt.network_ready():
            if DEBUG:
                print('GSM Network is READY :)')
        # -----------------------------------------------------------------------------------------------
        # # Dynamic Wait for Network and GPRS Ready
        # # MUST Buy Internet Package in SIM to use GPRS Or Command FAILED
        # if modem_mgnt.gprs_ready():
        #     if DEBUG:
        #         print('GPRS Network is READY :)')
        # -----------------------------------------------------------------------------------------------
        connect_to_cloud()
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("Entering in to Forever Loop...")
        # -----------------------------------------------------------------------------------------------


        # -----------------------------------------------------------------------------------------------
        while True:
            try:
                # ===============================================================================================
                # Reset the watchdog timer periodically to avoid restart
                # ===============================================================================================
                # sleep(1)
                wdt.feed()
                hb_counter += 1
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('hb_counter:', hb_counter)
                # -----------------------------------------------------------------------------------------------

                # ===============================================================================================
                # HB Sending Part
                # ===============================================================================================
                if hb_counter > hb_delay:
                    hb_counter = 0
                    hb_text = "hB"
                    # -----------------------------------------------------------------------------------------------
                    if send_flag_to_server_and_wait_for_reply(hb_text):
                        if DEBUG:
                            print("HB Update Success!")
                    # -----------------------------------------------------------------------------------------------
                    else:
                        if DEBUG:
                            print("HB Update FAILED!")
                # -----------------------------------------------------------------------------------------------

                # ===============================================================================================
                # Pending Alarm asking Part
                # ===============================================================================================
                pending_alrt_text = "gIveAlRTdatA"
                # -----------------------------------------------------------------------------------------------
                if send_flag_to_server_and_wait_for_reply(pending_alrt_text):
                    if DEBUG:
                        print("Pending Alert info asked Success!")
                    # -----------------------------------------------------------------------------------------------
                    # Split by comma into a list
                    reply_buff_list = reply_buff.decode().split("-")
                    # -----------------------------------------------------------------------------------------------
                    cmd_type = reply_buff_list[0]
                    alert_row_id = reply_buff_list[1]
                    dev_sl = reply_buff_list[2]
                    dev_name = reply_buff_list[3]
                    dev_alert_type = reply_buff_list[4]
                    alert_number = reply_buff_list[5]
                    phone_list = alert_number.split(",")  # Split by comma dynamically
                    alert_email = reply_buff_list[6]
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print("conf_buff_list:", reply_buff_list)
                        # -----------------------------------------------------------------------------------------------
                        print("cmd_type:", cmd_type)
                        print("alert_row_id:", alert_row_id)
                        print("dev_sl:", dev_sl)
                        print("dev_name:", dev_name)
                        print("dev_alert_type:", dev_alert_type)
                        # -----------------------------------------------------------------------------------------------
                        # print("alert_number:", alert_number)
                        for idx, number in enumerate(phone_list, start=1):
                            print(f"Phone[{idx}]. {number}")
                        # -----------------------------------------------------------------------------------------------
                        print("alert_email:", alert_email)
                    # -----------------------------------------------------------------------------------------------
                    if alert_row_id == 'NO_PENDING':
                        print("No Alert Call Pending :)")
                        sleep(1)
                    # -----------------------------------------------------------------------------------------------
                    else:
                        # Generate Call OR SMS
                        for number in phone_list:
                            if number:
                                modem_mgnt.call_to_a_mobile_no(number)
                                sleep(5)
                        # -----------------------------------------------------------------------------------------------
                        call_done_pkt = f"caLLdOnE,{alert_row_id}"
                        # Inform Server and Reset Status
                        if send_flag_to_server_and_wait_for_reply(call_done_pkt):
                            if DEBUG:
                                print("Call done and informed Server Success!")
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:while True:', e)
        # -----------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e:start_main_program:', e)
        machine.reset()
# ***********************************************************************************************


# -----------------------------------------------------------------------------------------------
start_main_program()
# -----------------------------------------------------------------------------------------------
