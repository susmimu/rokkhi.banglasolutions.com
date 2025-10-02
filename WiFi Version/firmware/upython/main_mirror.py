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
import camera
import wifi_manager
# -----------------------------------------------------------------------------------------------
# Pin definitions (same as #define in C)
PIR_PIN = 14  # MUST NOT change
AC_STATUS_PIN = 13
RELAY_PIN = 2
FLASH_LGT_PIN = 4  # Built-in flash
# -----------------------------------------------------------------------------------------------
SOCKET_TIMEOUT = 15
# -----------------------------------------------------------------------------------------------
motion_info_sent_to_server_f = False
hb_counter = 0
dev_sock = ''
mac_read = ''
change_conf_buff = ''
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
DEBUG = True
# -----------------------------------------------------------------------------------------------
wdt = WDT(timeout=180000)  # Enable it with a timeout of 180s / 3 Minutes
# -----------------------------------------------------------------------------------------------
"""
Examples:
p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
p0.on()                 # set pin to "on" (high) level
p0.off()                # set pin to "off" (low) level
p0.value(1)             # set pin to on/high

p2 = Pin(2, Pin.IN)     # create input pin on GPIO2
print(p2.value())       # get value, 0 or 1

p4 = Pin(4, Pin.IN, Pin.PULL_UP) # enable internal pull-up resistor
p5 = Pin(5, Pin.OUT, value=1) # set pin high on creation
p6 = Pin(6, Pin.OUT, drive=Pin.DRIVE_3) # set maximum drive strength
"""
# -----------------------------------------------------------------------------------------------
flash_lgt = Pin(FLASH_LGT_PIN, Pin.OUT, value=0)  # Initially Flash is OFF
# flash_lgt.off()
# flash_lgt.value(0)
# -----------------------------------------------------------------------------------------------
pir_sensor = Pin(PIR_PIN, Pin.IN)
# pir_sensor = Pin(PIR_PIN, Pin.IN, Pin.PULL_UP)
# pir_sensor = Pin(PIR_PIN, Pin.IN, Pin.PULL_DOWN)  # if you need INPUT_PULL DOWN
# -----------------------------------------------------------------------------------------------
ac_status = Pin(AC_STATUS_PIN, Pin.IN)
# ac_status = Pin(AC_STATUS_PIN, Pin.IN, Pin.PULL_DOWN)
# ac_status = Pin(AC_STATUS_PIN, Pin.IN, Pin.PULL_UP)  # if you need INPUT_PULL UP
# -----------------------------------------------------------------------------------------------
relay = Pin(RELAY_PIN, Pin.OUT, value=0)  # Initially Relay is OFF
# relay.value(0)
# -----------------------------------------------------------------------------------------------
dev_reboot_cnt = 0
cloud_domain = ''
cloud_ip = ''
cloud_port =''
device_sl = ''
hb_delay = ''
wifi_ssid = ''
wifi_pass = ''
motion_capture_active = ''
motion_capture_flash = ''
no_of_frame_capture_limit = ''
vdo_frame_size = ''
cam_flip = ''
cam_mirror = ''
light_alarm_status = ''
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def read_from_config_to_variable():
    # -----------------------------------------------------------------------------------------------
    global dev_reboot_cnt
    global cloud_domain
    global cloud_ip
    global cloud_port
    global device_sl
    global hb_delay
    global wifi_ssid
    global wifi_pass
    global motion_capture_active
    global motion_capture_flash
    global no_of_frame_capture_limit
    global vdo_frame_size
    global cam_flip
    global cam_mirror
    global light_alarm_status
    # -----------------------------------------------------------------------------------------------
    with open("config.json", "r") as f:
        data_in_config_file = ujson.load(f)
    # -----------------------------------------------------------------------------------------------
    dev_reboot_cnt = data_in_config_file["dev_reboot_cnt"]
    cloud_domain = data_in_config_file["cloud_domain"]
    cloud_ip = data_in_config_file["cloud_ip"]
    cloud_port = data_in_config_file["cloud_port"]
    device_sl = data_in_config_file["device_sl"]
    hb_delay = data_in_config_file["hb_delay"]
    wifi_ssid = data_in_config_file["ssid"]
    wifi_pass = data_in_config_file["password"]
    motion_capture_active = data_in_config_file["motion_capture_active"]
    motion_capture_flash = data_in_config_file["motion_capture_flash"]
    no_of_frame_capture_limit = data_in_config_file["no_of_frame_capture_limit"]
    vdo_frame_size = data_in_config_file["vdo_frame_size"]
    cam_flip = data_in_config_file["cam_flip"]
    cam_mirror = data_in_config_file["cam_mirror"]
    light_alarm_status = data_in_config_file["light_alarm_status"]
    # -----------------------------------------------------------------------------------------------
    if DEBUG:
        print("data_in_config_file:", data_in_config_file)
        # -----------------------------------------------------------------------------------------------
        print("dev_reboot_cnt:", dev_reboot_cnt)
        print("cloud_domain:", cloud_domain)
        print("cloud_ip:", cloud_ip)
        print("cloud_port:", cloud_port)
        print("device_sl:", device_sl)
        print("hb_delay:", hb_delay)
        print("wifi_ssid:", wifi_ssid)
        print("wifi_pass:", wifi_pass)
        print("motion_capture_active:", motion_capture_active)
        print("motion_capture_flash:", motion_capture_flash)
        print("no_of_frame_capture_limit:", no_of_frame_capture_limit)
        print("vdo_frame_size:", vdo_frame_size)
        print("cam_flip:", cam_flip)
        print("cam_mirror:", cam_mirror)
        print("light_alarm_status:", light_alarm_status)
    # -----------------------------------------------------------------------------------------------
# ***********************************************************************************************


# ***********************************************************************************************
def lic_check():
    try:
        global mac_read
        # ----------------------------------------------------------------------------------------
        # Read MAC from encrypted file
        f = open('hah_hah_ha.txt', 'rb')
        file_contents = f.read()
        f.close()
        f = ''
        # ----------------------------------------------------------------------------------------
        dec_key = ucryptolib.aes(b't8f9mx92c29499mb', 1)
        # ----------------------------------------------------------------------------------------
        decrypted_mac = dec_key.decrypt(file_contents).decode('utf-8')
        file_contents = ''
        dec_key = ''

        if DEBUG:
            print('decrypted_mac:', decrypted_mac)
        decrypted_mac_clean = ''

        for item in decrypted_mac:
            if 47 < ord(item) < 123:
                decrypted_mac_clean += item

        decrypted_mac = ''
        # ----------------------------------------------------------------------------------------
        mac_read = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode('utf-8')
        # ----------------------------------------------------------------------------------------
        if DEBUG:
            print('mac_read:', mac_read)

        if mac_read == decrypted_mac_clean:
            mac = ''
            decrypted_mac_clean = ''

            if DEBUG:
                print('License OK!')
        else:
            mac = ''
            decrypted_mac_clean = ''

            while True:
                # Show Lic Err on Display
                if DEBUG:
                    print('hah hah hah :)')

                sleep(15)
    except Exception as e:
        if DEBUG:
            print('e:lic_check():', e)

        flash_lgt.value(0)
        machine.reset()
# ***********************************************************************************************


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
        global cloud_domain, cloud_port, dev_sock
        # -----------------------------------------------------------------------------------------------
        # Connect to TCP server
        addr = socket.getaddrinfo(cloud_domain, cloud_port)[0][-1]
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
def login_to_cloud(dev_reboot_cnt_new):
    try:
        global device_sl, mac_read, dev_sock
        # -----------------------------------------------------------------------------------------------
        login_packet = device_sl + "," + mac_read + "," + str(dev_reboot_cnt_new)

        if DEBUG:
            print("Loging in to Cloud...")
            print("login_packet:", login_packet)
        # -----------------------------------------------------------------------------------------------
        dev_sock.send(login_packet.encode())  # encode() → convert to bytes
        # -----------------------------------------------------------------------------------------------
        login_reply_buff = dev_sock.recv(1024).decode()
        # -----------------------------------------------------------------------------------------------
        if 'lOgInOK' in login_reply_buff:
            if DEBUG:
                print("Cloud Login Success!")

            wifi_manager.flash_light_signal(4)
            return True
        else:
            if DEBUG:
                print("'lOgInOK' NOT Received\nRebooting...")

            machine.reset()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print("Cloud Login FAILED!\nRebooting...")
        print('e:connect_to_cloud:', e)
        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def send_flag_to_server_and_wait_for_reply(flag):
    try:
        global dev_sock, change_conf_buff
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
            reply_buff = dev_sock.recv(1024)
            # -----------------------------------------------------------------------------------------------
            if DEBUG:
                print("Received:", reply_buff.decode())
            # -----------------------------------------------------------------------------------------------
            if flag in reply_buff.decode():
                if flag == "hB":
                    # If Config Change in Server Reply; Server CMD Save in another buffer for processing
                    if 'cHngCONFIg' in reply_buff.decode():
                        change_conf_buff = ''
                        change_conf_buff = reply_buff.decode()
                # -----------------------------------------------------------------------------------------------
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
def detect_motion_by_pir():
    try:
        motion_pin_status = pir_sensor.value()  # Get value, 0 or 1
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("motion_pin_status: ", motion_pin_status)
        # -----------------------------------------------------------------------------------------------
        if motion_pin_status == 0:
            if DEBUG:
                print("MOTION DETECTED")

            return True
        # -----------------------------------------------------------------------------------------------
        else:
            if DEBUG:
                print("NO MOTION")

            return False
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG:
            print('e:detect_motion_by_pir:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def update_config(key, value, filename="config.json"):
    # Step 1: Load existing JSON
    try:
        with open(filename, "r") as f:
            config = ujson.load(f)
    except (OSError, ValueError):  # File not found or empty
        config = {}

    # Step 2: Update only one field
    config[key] = value

    # Step 3: Save back full JSON
    with open(filename, "w") as f:
        ujson.dump(config, f)
# ***********************************************************************************************


# ***********************************************************************************************
def execute_command_based_on_hb_reply(conf_buff):
    try:
        global light_alarm_status
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("conf_buff:", conf_buff)
        # -----------------------------------------------------------------------------------------------
        # Split by comma into a list
        conf_buff_list = conf_buff.split(",")

        if DEBUG:
            print("conf_buff_list:", conf_buff_list)
        # -----------------------------------------------------------------------------------------------
        cmd_type = conf_buff_list[2]
        # -----------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------
        if cmd_type == "dElaYhB":
            hb_delay_new = int(conf_buff_list[3])
            update_config("hb_delay", hb_delay_new)
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "w_SsIdPaSs":
            ssid_new = conf_buff_list[3]
            password_new = conf_buff_list[4]
            # -----------------------------------------------------------------------------------------------
            update_config("ssid", ssid_new)
            update_config("password", password_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "lgtAlrmChaLu":
            light_alarm_status = 1
            update_config("light_alarm_status", light_alarm_status)
            # -----------------------------------------------------------------------------------------------
            relay.value(1)

            if DEBUG:
                print('Load Relay ON')
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "lgtAlrmBOnDhO":
            light_alarm_status = 0
            update_config("light_alarm_status", light_alarm_status)
            # -----------------------------------------------------------------------------------------------
            relay.value(0)

            if DEBUG:
                print('Load Relay OFF')
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "CloUd_paraMs":
            cloud_domain_new = conf_buff_list[3]
            cloud_ip_new = conf_buff_list[4]
            cloud_port_new = int(conf_buff_list[5])
            # -----------------------------------------------------------------------------------------------
            update_config("cloud_domain", cloud_domain_new)
            update_config("cloud_ip", cloud_ip_new)
            update_config("cloud_port", cloud_port_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "dEv_sL":
            device_sl_new = conf_buff_list[3]
            # -----------------------------------------------------------------------------------------------
            update_config("device_sl", device_sl_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "hb_interval":
            hb_delay_new = int(conf_buff_list[1])
            # -----------------------------------------------------------------------------------------------
            with open("config.json", "w") as f:
                ujson.dump({"hb_delay": hb_delay_new}, f)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "mOtioNcONf":
            motion_capture_active_new = conf_buff_list[3]
            # -----------------------------------------------------------------------------------------------
            if motion_capture_active_new == 'MaS_On':
                motion_capture_active_new = 1
            elif motion_capture_active_new == 'MaS_oFF':
                motion_capture_active_new = 0
            # -----------------------------------------------------------------------------------------------
            motion_capture_flash_new = conf_buff_list[4]
            # -----------------------------------------------------------------------------------------------
            if motion_capture_flash_new == 'mcf_oN':
                motion_capture_flash_new = 1
            elif motion_capture_flash_new == 'mcf_OfF':
                motion_capture_flash_new = 0
            # -----------------------------------------------------------------------------------------------
            no_of_frame_capture_limit_new = int(conf_buff_list[5])
            vdo_frame_size_new = int(conf_buff_list[6])
            # -----------------------------------------------------------------------------------------------
            update_config("motion_capture_active", motion_capture_active_new)
            update_config("motion_capture_flash", motion_capture_flash_new)
            update_config("no_of_frame_capture_limit", no_of_frame_capture_limit_new)
            update_config("vdo_frame_size", vdo_frame_size_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "cAmIniT":
            cam_flip_new = int(conf_buff_list[3])
            cam_mirror_new = int(conf_buff_list[4])
            # -----------------------------------------------------------------------------------------------
            update_config("cam_flip", cam_flip_new)
            update_config("cam_mirror", cam_mirror_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "cApPiC":
            resolution = int(conf_buff_list[3])
            quality = int(conf_buff_list[4])
            extra_flash = int(conf_buff_list[5])

            if DEBUG:
                print('resolution:', resolution)
                print('quality:', quality)
                print('extra_flash:', extra_flash)
            # -----------------------------------------------------------------------------------------------
            global flash_lgt, cam_flip, cam_mirror
            img_capture_and_sent_ok_f = False
            # Control FLASH-Light
            if extra_flash:
                flash_lgt.on()

                if DEBUG:
                    print("Flash Light ON")
            # -----------------------------------------------------------------------------------------------
            else:
                flash_lgt.off()

                if DEBUG:
                    print("Flash Light OFF")
            # -----------------------------------------------------------------------------------------------
            try:
                camera.deinit()

                if DEBUG:
                    print('camera.deinit() OK!')
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                if DEBUG:
                    print('e:camera.deinit() FAILED!:', e)
            # -----------------------------------------------------------------------------------------------
            try:
                camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
                camera.flip(cam_flip)
                camera.mirror(cam_mirror)
                camera.framesize(resolution)
                camera.quality(quality)
                sleep(1)
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('camera.init() SUCCESS!')
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                if DEBUG:
                    print('e:camera.init() FAILED!', e)
            # -----------------------------------------------------------------------------------------------
            # Capture Image for 10 Times for better Quality
            img_buff = ''

            for i in range(10):
                img_buff = ''
                img_buff = camera.capture()
            # -----------------------------------------------------------------------------------------------
            flash_lgt.off()

            if DEBUG:
                print("Flash Light OFF")
                print("Image size:", len(img_buff), "bytes, ", (len(img_buff) / 1024), "KB")
            # -----------------------------------------------------------------------------------------------
            # Send image length first
            img_len_with_marker = "imglen," + str(len(img_buff))  # send size as text
            # -----------------------------------------------------------------------------------------------
            if send_flag_to_server_and_wait_for_reply(img_len_with_marker):
                if DEBUG:
                    print(img_len_with_marker, "Sent Successfully\nSending 'img_buff'...")

                # Send image data
                dev_sock.send(img_buff)

                if DEBUG:
                    print("'img_buff' sent success!\nWaiting for server confirmation...")
                # -----------------------------------------------------------------------------------------------
                try:
                    img_saver_by_server_buff = dev_sock.recv(32)

                    if DEBUG:
                        print("img_saver_by_server_buff:", img_saver_by_server_buff)
                        print("img_saver_by_server_buff_Decoded:", img_saver_by_server_buff.decode())
                    # -----------------------------------------------------------------------------------------------
                    if img_saver_by_server_buff.decode() == 'sImgRcvd':
                        img_capture_and_sent_ok_f = True

                        if DEBUG:
                            print("Image saved by Server Success!")
                # -----------------------------------------------------------------------------------------------
                except socket.timeout:
                    if DEBUG:
                        print("Timeout:'img_saver_by_server_buff':", SOCKET_TIMEOUT, "seconds")
                # -----------------------------------------------------------------------------------------------
                except Exception as e:
                    print("e:", e)
            # -----------------------------------------------------------------------------------------------
            else:
                if DEBUG:
                    print(img_len_with_marker, "Sent FAILED")
            # -----------------------------------------------------------------------------------------------
            # Camera Init to its Original Stage
            if DEBUG:
                print("Restoring Camera settings for Motion VDO Capture...")
            # -----------------------------------------------------------------------------------------------
            try:
                camera.deinit()

                if DEBUG:
                    print('camera.deinit() OK!')
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                if DEBUG:
                    print('e:camera.deinit():', e)
                    print('camera.deinit() FAILED!')
            # -----------------------------------------------------------------------------------------------
            try:
                camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
                camera.flip(cam_flip)
                camera.mirror(cam_mirror)
                camera.framesize(vdo_frame_size)
                camera.quality(10)
                sleep(1)
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('camera.init() SUCCESS!')
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                if DEBUG:
                    print('e:camera.init():', e)
                    print('camera.init() FAILED!\nRebooting...')
                # -----------------------------------------------------------------------------------------------
                machine.reset()
            # -----------------------------------------------------------------------------------------------
            flash_lgt.off()

            if DEBUG:
                print("Flash Light OFF")
            # -----------------------------------------------------------------------------------------------
            return img_capture_and_sent_ok_f
        # -----------------------------------------------------------------------------------------------
        elif cmd_type == "rsTrEbooTcNt":
            dev_reboot_cnt_new = 0
            update_config("dev_reboot_cnt", dev_reboot_cnt_new)
            # -----------------------------------------------------------------------------------------------
            return True
        # -----------------------------------------------------------------------------------------------
        return False
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG:
            print('e:execute_command_based_on_hb_reply:', e)
            print('e:update_device_config FAILED:', e)
        # -----------------------------------------------------------------------------------------------
        return False
# ***********************************************************************************************


# ***********************************************************************************************
def goto_forever_loop():
    # -----------------------------------------------------------------------------------------------
    global hb_counter, motion_info_sent_to_server_f, change_conf_buff
    # -----------------------------------------------------------------------------------------------
    if DEBUG:
        print("Entering in to Forever Loop...")
    # -----------------------------------------------------------------------------------------------
    while True:
        try:
            # ===============================================================================================
            # Reset the watchdog timer periodically to avoid restart
            # ===============================================================================================
            sleep(1)
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
                    if change_conf_buff:
                        if execute_command_based_on_hb_reply(change_conf_buff):
                            change_conf_buff = ''
                            read_from_config_to_variable()

                            if DEBUG:
                                print("Device Config Update Success!\nInforming to Server...")
                            # -----------------------------------------------------------------------------------------------
                            try:
                                dev_sock.send("cOnFS".encode())  # encode() → convert to bytes
                            except ExceptionGroup as e:
                                print('e:', e)
                            # -----------------------------------------------------------------------------------------------
                            if DEBUG:
                                print("Server Successfully Informed!")
                        # -----------------------------------------------------------------------------------------------
                        else:
                            if DEBUG:
                                print("Device Config Update FAILED!")
                # -----------------------------------------------------------------------------------------------
                else:
                    if DEBUG:
                        print("HB Update FAILED!")
            # -----------------------------------------------------------------------------------------------

            # ===============================================================================================
            # Motion Detection and Capture Part
            # ===============================================================================================
            if motion_capture_active:
                while detect_motion_by_pir():
                    # -----------------------------------------------------------------------------------------------
                    motion_info_sent_to_server_f = False
                    server_confirmed_start_img_flag = False
                    total_no_of_frames = 0
                    hb_counter = 0
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print("=================================================================")
                        print("Motion Detected! Informing the Server and Waiting for response...")
                    # -----------------------------------------------------------------------------------------------
                    # Only execute if "motion_info_sent_to_server_f" is False to prevent multiple try
                    if not motion_info_sent_to_server_f:
                        if send_flag_to_server_and_wait_for_reply("MoTionYeS"):
                            if DEBUG:
                                print("Server successfully informed about Motion :)")
                            # -----------------------------------------------------------------------------------------------
                            # Set the Flag. So prevent multiple execution
                            motion_info_sent_to_server_f = True
                        # -----------------------------------------------------------------------------------------------
                        else:
                            if DEBUG:
                                print('Reply NOT as: "MoTionYeS"')
                    # -----------------------------------------------------------------------------------------------

                    # -----------------------------------------------------------------------------------------------
                    # Server Already informed about Motion
                    if motion_info_sent_to_server_f:
                        if DEBUG:
                            print("Tell Server to Save Images and Waiting for response...")
                        # -----------------------------------------------------------------------------------------------
                        if send_flag_to_server_and_wait_for_reply("mOtImGsTaRt"):
                            if DEBUG:
                                print("Server successfully informed to Save Images")
                            # -----------------------------------------------------------------------------------------------
                            server_confirmed_start_img_flag = True
                        # -----------------------------------------------------------------------------------------------
                        else:
                            if DEBUG:
                                print('Reply NOT as: "mOtImGsTaRt"')
                    # -----------------------------------------------------------------------------------------------

                    # -----------------------------------------------------------------------------------------------
                    # Server is Ready to Receive and Save ImageFrames
                    if server_confirmed_start_img_flag:
                        # -----------------------------------------------------------------------------------------------
                        # Control FLASH-Light
                        if motion_capture_flash:
                            flash_lgt.on()

                            if DEBUG:
                                print("Flash Light ON")
                        # -----------------------------------------------------------------------------------------------
                        else:
                            flash_lgt.off()

                            if DEBUG:
                                print("Flash Light OFF")
                        # -----------------------------------------------------------------------------------------------
                        while detect_motion_by_pir() and (total_no_of_frames < no_of_frame_capture_limit):
                            img_buff = camera.capture()
                            # -----------------------------------------------------------------------------------------------
                            if not img_buff:
                                break
                            else:
                                if DEBUG:
                                    print("Image size:", len(img_buff), "bytes, ", (len(img_buff) / 1024), "KB")
                                # -----------------------------------------------------------------------------------------------
                                # Send image length first
                                img_len_with_marker = "imglen," + str(len(img_buff))  # send size as text
                                # -----------------------------------------------------------------------------------------------
                                if send_flag_to_server_and_wait_for_reply(img_len_with_marker):
                                    if DEBUG:
                                        print(img_len_with_marker, "Sent Successfully")

                                    # Send image data
                                    dev_sock.send(img_buff)
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print("Single Image sent successfully!\nWaiting for server confirmation...")
                                        print("-----------------------------------------------------------------")
                                    # -----------------------------------------------------------------------------------------------
                                    try:
                                        sImgRcvd_buff = dev_sock.recv(32)

                                        if DEBUG:
                                            print("sImgRcvd_buff:", sImgRcvd_buff)
                                            print("sImgRcvd_buff_Decoded:", sImgRcvd_buff.decode())
                                        # -----------------------------------------------------------------------------------------------
                                        if sImgRcvd_buff.decode() == 'sImgRcvd':
                                            if DEBUG:
                                                print("Single Image saved by Server Success!")

                                            total_no_of_frames += 1

                                            if DEBUG:
                                                print("total_no_of_frames: ", total_no_of_frames)
                                    # -----------------------------------------------------------------------------------------------
                                    except socket.timeout:
                                        if DEBUG:
                                            print("Timeout:'sImgRcvd':", SOCKET_TIMEOUT, "seconds")

                                        sleep(1)
                                    # -----------------------------------------------------------------------------------------------
                                    except Exception as e:
                                        print("e:", e)
                                # -----------------------------------------------------------------------------------------------
                                else:
                                    if DEBUG:
                                        print(img_len_with_marker, "Sent FAILED")
                        # -----------------------------------------------------------------------------------------------
                        # Motion END, or Frame Limit Reached. Upper Loop Broken. Inform Server that no more Motion Image Left
                        flash_lgt.off()

                        if DEBUG:
                            print("Flash Light OFF")
                            print("All Frames Sent! Telling Server to STOP Saving and Waiting for response...")
                        # -----------------------------------------------------------------------------------------------
                        # sleep(3)
                        if send_flag_to_server_and_wait_for_reply("eNdM"):
                            if DEBUG:
                                print("Server successfully informed to Stop Saving :)")
                            # -----------------------------------------------------------------------------------------------
                            # A small delay for next motion frames
                            sleep(1)
                        # -----------------------------------------------------------------------------------------------
                        else:
                            if DEBUG:
                                print('Reply NOT as: "eNdM"')
            # -----------------------------------------------------------------------------------------------
            else:
                if DEBUG:
                    print("Motion Alert NOT Activated")
                # -----------------------------------------------------------------------------------------------
                flash_lgt.value(0)
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:goto_forever_loop:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def start_main_program():
    try:
        # -----------------------------------------------------------------------------------------------
        read_from_config_to_variable()
        # -----------------------------------------------------------------------------------------------
        dev_reboot_cnt_new = int(dev_reboot_cnt) + 1
        update_config("dev_reboot_cnt", dev_reboot_cnt_new)
        # -----------------------------------------------------------------------------------------------
        lic_check()
        # -----------------------------------------------------------------------------------------------
        show_hardware_info()
        # -----------------------------------------------------------------------------------------------
        if DEBUG:
            print("Single Flash to Check Power!")
        # -----------------------------------------------------------------------------------------------
        wifi_manager.flash_light_signal(1)
        # -----------------------------------------------------------------------------------------------
        wifi_manager.reset_wifi(1)
        wifi_conn_status = wifi_manager.connect_to_wifi(wifi_ssid, wifi_pass, 30)
        # -----------------------------------------------------------------------------------------------
        if wifi_conn_status:
            wifi_manager.flash_light_signal(2)
        # -----------------------------------------------------------------------------------------------
        try:
            camera.deinit()

            if DEBUG:
                print('camera.deinit() OK!')
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            if DEBUG:
                print('e:camera.deinit():', e)
                print('camera.deinit() FAILED!')
        # -----------------------------------------------------------------------------------------------
        try:
            camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
            camera.flip(cam_flip)
            camera.mirror(cam_mirror)
            camera.framesize(vdo_frame_size)
            # 1 = 160x120, 2 = 176x144, 3 = 240x176, 4 = 240x240, 5 = 320x240, 6 = 400x296, 7 = 480x320, 8 = 640x480,
            # 9 = 800x600, 10 = 1024x768, 11 = 1280x720, 12 = 1280x1024, 13 = 1600x1200  (This is the Max Value)
            camera.quality(10)
            # 4~63, Lower the value higher the quality
            sleep(1)

            if DEBUG:
                print('camera.init() SUCCESS!')
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            if DEBUG:
                print('e:camera.init():', e)
                print('camera.init() FAILED!\nRebooting...')
            # -----------------------------------------------------------------------------------------------
            machine.reset()
        # -----------------------------------------------------------------------------------------------
        # Restoring Lod Relay based on its Last state
        if light_alarm_status:
            relay.value(1)

            if DEBUG:
                print('Load Relay ON')
        else:
            relay.value(0)

            if DEBUG:
                print('Load Relay OFF')
        # -----------------------------------------------------------------------------------------------
        connect_to_cloud()
        sleep(3)    # If no delay LED Blink can not view properly
        # -----------------------------------------------------------------------------------------------
        if login_to_cloud(dev_reboot_cnt_new):
            goto_forever_loop()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e:start_main_program:', e)
        flash_lgt.value(0)
        machine.reset()
# ***********************************************************************************************


# -----------------------------------------------------------------------------------------------
start_main_program()
# -----------------------------------------------------------------------------------------------
