#!/usr/bin/python3
# -----------------------------------------------------------------------------------------------
from datetime import datetime, timedelta, time
from threading import Lock, Thread
import pytz
import datetime
import socket
import time
import sys
import sqlite3
import re
import os
import subprocess
# -----------------------------------------------------------------------------------------------
db_path = '/home/just/rokkhi.banglasolutions.com/client_software/proj_rokkhi_banglasolutions_com_db.sqlite3'
# -----------------------------------------------------------------------------------------------
img_file_path = '/home/just/rokkhi.banglasolutions.com/client_software/media/'
vdo_file_path = '/home/just/rokkhi.banglasolutions.com/client_software/media/'
# -----------------------------------------------------------------------------------------------
HOST_IP = 'rokkhi.banglasolutions.com'
HOST_PORT = 6237
thread_counter = 0
# Create a list in which threads will be stored in order to be joined later
client_thread_list = []
DEFAULT_TIMEOUT = 30
# -----------------------------------------------------------------------------------------------
DEBUG = True
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
class ClientThread(Thread):
    # ***********************************************************************************************
    def __init__(self, client_socket, address, timeout):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.timeout = timeout
        # -----------------------------------------------------------------------------------------------
        self.data = None
        self.login_ok_flag = None
        self.dev_sl = None
        self.esp_mac = None
        self.dev_reboot_cnt = None
        self.all_motion_images_received_flag = None
        # -----------------------------------------------------------------------------------------------
    # ***********************************************************************************************


    # ***********************************************************************************************
    def run(self):
        global thread_counter
        # -----------------------------------------------------------------------------------------------
        # Device Login Part
        thread_counter += 1

        if DEBUG:
            print('New Device Connected :)')
            print('New Thread CREATED\nTotal running thread(s): ', thread_counter)
        # -----------------------------------------------------------------------------------------------
        self.device_login()
        # -----------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------
        previous_state = None
        current_state = None
        tz = pytz.timezone("Asia/Dhaka")
        # Infinite Loop if LogIn Success
        while self.login_ok_flag:
            # ===============================================================================================
            # In this Part, Device Registration and Validity Checks in Real time and Break Loop if necessary
            # -----------------------------------------------------------------------------------------------
            if not self.check_device_active_status():
                break
            # ===============================================================================================


            # ===============================================================================================
            # HB and Motion Image Receiving Part
            # Command receives here with a very small Timeout
            # Dynamically change Timeout 3 Sec ~ DEFAULT_TIMEOUT
            # -----------------------------------------------------------------------------------------------
            try:
                # -----------------------------------------------------------------------------------------------
                self.data = self.client_socket.recv(64)
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('self.data: RAW --->:', self.data)
                # -----------------------------------------------------------------------------------------------
                if not self.data:
                    break
                # -----------------------------------------------------------------------------------------------
                self.data = self.data.decode().strip()
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('self.data Striped: --->:', self.data)
                # -----------------------------------------------------------------------------------------------

                # -----------------------------------------------------------------------------------------------
                if self.data == 'hB':
                    if DEBUG:
                        print('HB received from:', str(self.dev_sl), 'Replying to device...')
                    # -----------------------------------------------------------------------------------------------
                    if self.update_hb_info():
                        if DEBUG:
                            print(self.dev_sl, ':', 'HB update Success!')
                        # ===============================================================================================
                        # Read if any pending CMD for this Device, Then Concat and then Reply
                        # ===============================================================================================
                        # Read CMD from DB to set the HB Delay
                        cmd_status_hb_delay, cmd_name, hb_delay = self.read_hb_delay_cmd()
                        # print('cmd_status_hb_delay, cmd_name, hb_delay:', cmd_status_hb_delay, cmd_name, hb_delay)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB to Activate/ Deactivate Motion and Flash-Light
                        cmd_status_motion_flash, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size = self.read_motion_capture_params()
                        # print('cmd_status_motion_flash, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size:', cmd_status_motion_flash, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB for Camera Init Parameters
                        cmd_status_cam_init, cam_init_cmd_name, is_cam_flip, is_cam_mirror = self.read_camera_init_params()
                        # print('cmd_status_cam_init, cam_init_cmd_name, is_cam_flip, is_cam_mirror:', cmd_status_cam_init, cam_init_cmd_name, is_cam_flip, is_cam_mirror)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB for WiFi SSID Pass
                        cmd_status_ssid_pass, ssid_pass_cmd_name, wifi_ssid, wifi_pass = self.read_wifi_ssid_pass()
                        # print('cmd_status_ssid_pass, ssid_pass_cmd_name, wifi_ssid, wifi_pass:', cmd_status_ssid_pass, ssid_pass_cmd_name, wifi_ssid, wifi_pass)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB for Cloud IP, Domain, Port
                        cmd_status_cloud_params, cp_cmd_name, domain_name, ip_address, cloud_port = self.read_cloud_parameters()
                        # print('cmd_status_cloud_params, cp_cmd_name, domain_name, ip_address, cloud_port:', cmd_status_cloud_params, cp_cmd_name, domain_name, ip_address, cloud_port)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD for Light-Alarm ON from DB
                        cmd_status_alarm_on = self.read_light_alarm_on_cmd()
                        # print('Light-Alarm ON: cmd_status_alarm_on:', cmd_status_alarm_on)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD for Light-Alarm OFF from DB
                        cmd_status_alarm_off = self.read_light_alarm_off_cmd()
                        # print('Light-Alarm OFF: cmd_status_alarm_off:', cmd_status_alarm_off)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB for Taking Photo Manually
                        cmd_status_cap_img, flashlight, resolution, resolution_visual = self.read_manual_image_capture_cmd()
                        # print('cmd_status_cap_img, flashlight, resolution, resolution_visual: ', cmd_status_cap_img, flashlight, resolution, resolution_visual)
                        # -----------------------------------------------------------------------------------------------
                        # Read CMD from DB for Reboot Counter Reset
                        cmd_status_rc, cmd_name_rc = self.read_reboot_cnt_reset_cmd()
                        # print('cmd_status_rc, cmd_name_rc: ', cmd_status_rc, cmd_name_rc)
                        # -----------------------------------------------------------------------------------------------

                        # ===============================================================================================
                        # Execution Starting for Pending Command
                        # ===============================================================================================
                        if cmd_status_hb_delay == 'processing':
                            if self.set_hb_delay(cmd_name, hb_delay):
                                if DEBUG:
                                    print('HB Delay Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_motion_flash == 'processing':
                            if self.set_motion_capture_params(is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size):
                                if DEBUG:
                                    print('Motion Config Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_cam_init == 'processing':
                            if self.set_cam_init_params(cam_init_cmd_name, is_cam_flip, is_cam_mirror):
                                if DEBUG:
                                    print('Camera Init Params Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_ssid_pass == 'processing':
                            if self.set_wifi_ssid_password(ssid_pass_cmd_name, wifi_ssid, wifi_pass):
                                if DEBUG:
                                    print('SSID Password Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_cloud_params == 'processing':
                            if self.set_cloud_parameters(cp_cmd_name, domain_name, ip_address, cloud_port):
                                if DEBUG:
                                    print('Domain, IP, Port Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_alarm_on == 'processing':
                            if self.set_light_alarm_on():
                                if DEBUG:
                                    print('Light-Alarm ON Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_alarm_off == 'processing':
                            if self.set_light_alarm_off():
                                if DEBUG:
                                    print('Light-Alarm OFF Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_cap_img == 'processing':
                            if self.set_manual_image_capture(flashlight, resolution):
                                if DEBUG:
                                    print('Manual Capture Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        elif cmd_status_rc == 'processing':
                            if self.set_reboot_cnt_reset_cmd(cmd_name_rc):
                                if DEBUG:
                                    print('Reset Reboot Counter Set Success!')
                        # -----------------------------------------------------------------------------------------------
                        else:
                            self.client_socket.send(self.data.encode())
                    # -----------------------------------------------------------------------------------------------
                    else:
                        if DEBUG:
                            print(self.dev_sl, ':', 'HB update Failed!')
                        # -----------------------------------------------------------------------------------------------
                        break
                # -----------------------------------------------------------------------------------------------
                elif self.data == 'MoTionYeS':
                    if DEBUG:
                        print('======================================================================')
                        print('Motion Detected Flag received. Replying clint...', self.data)
                    # -----------------------------------------------------------------------------------------------
                    self.client_socket.send(self.data.encode())
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print('Now Blocked to receive "mOtImGsTaRt"')
                    # -----------------------------------------------------------------------------------------------
                    self.data = self.client_socket.recv(64)
                    # -----------------------------------------------------------------------------------------------
                    if not self.data:
                        break
                    # -----------------------------------------------------------------------------------------------
                    else:
                        self.data = self.data.decode().strip()
                        # -----------------------------------------------------------------------------------------------
                        if DEBUG:
                            print('self.data: ---> 02:', self.data)
                    # -----------------------------------------------------------------------------------------------
                    if self.data == 'mOtImGsTaRt':
                        if DEBUG:
                            print('Motion image Start Flag received.\nReplying clint...', self.data)
                        # -----------------------------------------------------------------------------------------------
                        self.client_socket.send(self.data.encode())
                        # -----------------------------------------------------------------------------------------------
                        # Receive all images Here. Create file name and path
                        current_vdo_captured_timestamp = int(time.time())
                        ts = str(current_vdo_captured_timestamp)
                        # -----------------------------------------------------------------------------------------------
                        motion_vdos_path = vdo_file_path + str(self.dev_sl) + '/motion_vdos'
                        os.makedirs(motion_vdos_path, exist_ok=True)
                        motion_file_name = open(f"{motion_vdos_path}/{ts}.mjpeg", "wb")
                        total_frame = 0
                        self.all_motion_images_received_flag = False
                        # -----------------------------------------------------------------------------------------------
                        while True:
                            if DEBUG:
                                print('Blocked to receive Images')
                            # -----------------------------------------------------------------------------------------------
                            self.data = self.client_socket.recv(32)
                            # -----------------------------------------------------------------------------------------------
                            if not self.data:
                                break
                            # -----------------------------------------------------------------------------------------------
                            else:
                                img_len_with_marker = self.data.decode().strip()
                                # -----------------------------------------------------------------------------------------------
                                if DEBUG:
                                    print('img_len_with_marker:', img_len_with_marker)
                                # -----------------------------------------------------------------------------------------------
                                if img_len_with_marker.startswith("imglen,"):
                                    # Extract size as integer
                                    img_size = int(img_len_with_marker.split(",")[1])
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print("Image size:", img_size)
                                    # -----------------------------------------------------------------------------------------------
                                    image_data = b""
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print('Loop until ', img_size, 'bytes received...')
                                    # Echo back the same data (acknowledgment)
                                    self.client_socket.send(self.data)  # send back what we received
                                    # -----------------------------------------------------------------------------------------------
                                    while len(image_data) < img_size:
                                        packet = self.client_socket.recv(4096)
                                        # -----------------------------------------------------------------------------------------------
                                        if not packet:
                                            break
                                        # -----------------------------------------------------------------------------------------------
                                        image_data += packet
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print("A single image FULLY received. Size (bytes):", len(image_data))
                                    # -----------------------------------------------------------------------------------------------
                                    # Save image to file
                                    motion_file_name.write(image_data)
                                    motion_file_name.write(bytes([0xFF, 0xD9]))  # End of JPEG marker
                                    total_frame += 1
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print("Confirming Client...")
                                    # -----------------------------------------------------------------------------------------------
                                    self.client_socket.send("sImgRcvd".encode())
                                # -----------------------------------------------------------------------------------------------
                                elif img_len_with_marker == 'eNdM':
                                    if DEBUG:
                                        print('All motion Images receive completed. Breaking the Loop...')
                                    # -----------------------------------------------------------------------------------------------
                                    self.all_motion_images_received_flag = True
                                    # break
                                    # -----------------------------------------------------------------------------------------------
                                    motion_file_name.close()
                                    # -----------------------------------------------------------------------------------------------
                                    # *** CONVERT .mjpeg to .mp4 file
                                    vdo_path = motion_vdos_path + '/' + ts + '.mjpeg'
                                    mp4_path = motion_vdos_path + '/' + ts + '.mp4'
                                    vdo_info_for_db = str(self.dev_sl) + '/motion_vdos/' + ts + '.mp4'
                                    threshold_kb = 20
                                    # -----------------------------------------------------------------------------------------------
                                    if DEBUG:
                                        print('vdo_path:', vdo_path)
                                        print('mp4_path:', mp4_path)
                                        print('vdo_info_for_db:', vdo_info_for_db)
                                    # -----------------------------------------------------------------------------------------------
                                    if self.all_motion_images_received_flag:
                                        # Check if file exists
                                        if os.path.isfile(vdo_path):
                                            # Check file size
                                            size_kb = os.path.getsize(vdo_path) / 1024  # Convert bytes to KB
                                            # -----------------------------------------------------------------------------------------------
                                            if size_kb < threshold_kb:
                                                # Delete file less than 50 KB
                                                os.remove(vdo_path)
                                                # -----------------------------------------------------------------------------------------------
                                                if DEBUG:
                                                    print(f"Deleted {vdo_path} ({size_kb:.2f} KB)")
                                            # -----------------------------------------------------------------------------------------------
                                            else:
                                                if DEBUG:
                                                    print(f"{vdo_path} file size is > {threshold_kb} KB. Converting to .mp4 format...")
                                                # -----------------------------------------------------------------------------------------------
                                                self.convert_mjpeg_to_mp4_and_cleanup(vdo_path, mp4_path)
                                                # Delete the *.mjpeg file
                                                try:
                                                    os.remove(vdo_path)
                                                    # -----------------------------------------------------------------------------------------------
                                                    if DEBUG:
                                                        print(f"After convertion, the file {vdo_path} DELETED")
                                                # -----------------------------------------------------------------------------------------------
                                                except Exception as e:
                                                    print('e:FD: ', e)
                                                # -----------------------------------------------------------------------------------------------
                                                video_size = os.path.getsize(mp4_path) / 1024  # Convert bytes to KB
                                                # -----------------------------------------------------------------------------------------------
                                                if DEBUG:
                                                    print('video_size: ', video_size)
                                                    print('total_frame: ', total_frame)
                                                # -----------------------------------------------------------------------------------------------
                                                if video_size < 10:
                                                    # Delete file if less than 10 KB
                                                    os.remove(mp4_path)
                                                    # -----------------------------------------------------------------------------------------------
                                                    if DEBUG:
                                                        print(f"Deleted {mp4_path} (Size is < 10KB)")
                                                # -----------------------------------------------------------------------------------------------
                                                else:
                                                    # Read Snooze value for this device from DB
                                                    snooze_val_in_db = self.read_snooze_value_for_this_device()
                                                    # -----------------------------------------------------------------------------------------------
                                                    if DEBUG:
                                                        print(f"Snooze delay: {snooze_val_in_db} Minutes")
                                                    # -----------------------------------------------------------------------------------------------
                                                    # Read from Last file name which one was MUST NOT in Snoozed Status
                                                    # Else many continuous captures will be as Snooze Status
                                                    last_captured_file_name = self.read_ts_from_last_unsnoozed_file_name()
                                                    # -----------------------------------------------------------------------------------------------
                                                    if DEBUG:
                                                        print("last_captured_file_name:", last_captured_file_name)
                                                    # -----------------------------------------------------------------------------------------------
                                                    is_alert_snooze = False
                                                    # -----------------------------------------------------------------------------------------------
                                                    if last_captured_file_name:
                                                        # In case of 1st capture it will geg blank
                                                        last_captured_ts = int(last_captured_file_name.split("/")[-1].split(".")[0])
                                                        # Calculate Duration Between Last VDO and Current VDO
                                                        duration_seconds = current_vdo_captured_timestamp - last_captured_ts
                                                        duration_minutes = int(duration_seconds / 60)
                                                        # -----------------------------------------------------------------------------------------------
                                                        if DEBUG:
                                                            print("last_captured_ts:", last_captured_ts)
                                                            print("Duration (seconds):", duration_seconds)
                                                            print("Duration (minutes):", duration_minutes)
                                                        # -----------------------------------------------------------------------------------------------
                                                        if duration_minutes < snooze_val_in_db:
                                                            # 5 Minutes or More time Passed. So, No Snooze
                                                            is_alert_snooze = True
                                                        # -----------------------------------------------------------------------------------------------
                                                        if self.insert_motion_vdo_info_to_db(video_size, total_frame, vdo_info_for_db, is_alert_snooze):
                                                            if DEBUG:
                                                                print('Image info saved in DB success!')
                                                        # -----------------------------------------------------------------------------------------------
                                                        else:
                                                            if DEBUG:
                                                                print('Image info saved in DB FAILED!')
                                                    # -----------------------------------------------------------------------------------------------
                                                    else:
                                                        if self.insert_motion_vdo_info_to_db(video_size, total_frame, vdo_info_for_db, is_alert_snooze):
                                                            if DEBUG:
                                                                print('Image info saved in DB success!')
                                                        # -----------------------------------------------------------------------------------------------
                                                        else:
                                                            if DEBUG:
                                                                print('Image info saved in DB FAILED!')
                                        # -----------------------------------------------------------------------------------------------
                                        else:
                                            if DEBUG:
                                                print(f"{vdo_path} does not exist.")
                                    # -----------------------------------------------------------------------------------------------
                                    else:
                                        # DELETE Partially Received *.mjpeg file
                                        try:
                                            os.remove(vdo_path)
                                            # -----------------------------------------------------------------------------------------------
                                            if DEBUG:
                                                print("Partially Received *.mjpeg file DELETED")
                                            # -----------------------------------------------------------------------------------------------
                                            break
                                        # -----------------------------------------------------------------------------------------------
                                        except Exception as e:
                                            print("e:PI: ", e)
                                    # -----------------------------------------------------------------------------------------------                                    # Send Confirmation to the Client
                                    self.client_socket.send("eNdM".encode())
                                    break
                        # -----------------------------------------------------------------------------------------------
                        self.data = ''
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:Breaking the while Loop:', e)
                self.data = ''
                break
            # ===============================================================================================


            # ===============================================================================================
            # Device Working Mode (Motion Capture Active / Deactivate) is Control here
            # In this part, Service will update DB Value
            # -----------------------------------------------------------------------------------------------
            try:
                # -----------------------------------------------------------------------------------------------
                # Read Motion Alert Mode and Time
                dev_active_mode, dev_active_hour_start, dev_active_hour_end, change_pending = self.read_motion_mode_and_active_schedule()
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('dev_active_mode, dev_active_hour_start, dev_active_hour_end, change_pending: ', dev_active_mode, dev_active_hour_start, dev_active_hour_end, change_pending)
                # -----------------------------------------------------------------------------------------------
                """
                01. SET Motion Capture Active Flag in DB
                02. SET Status to "processing"
                03. Then HB will Send Command to Device at next HB which is Safer
                04. CLEAR "change_pending" Flag to prevent Multiple execution
                """
                # -----------------------------------------------------------------------------------------------
                if dev_active_mode == 'always_on' and change_pending:
                    if DEBUG:
                        print("dev_active_mode:", dev_active_mode)
                    # -----------------------------------------------------------------------------------------------
                    if self.activate_motion_capture_and_set_status_to_processing():
                        if DEBUG:
                            print('self.activate_motion_capture_and_set_status_to_processing(): Success!')
                        # -----------------------------------------------------------------------------------------------
                        if self.clear_change_pending_flag():
                            if DEBUG:
                                print('self.clear_change_pending_flag(): OK!')
                # -----------------------------------------------------------------------------------------------
                elif dev_active_mode == 'always_off' and change_pending:
                    if DEBUG:
                        print("dev_active_mode:", dev_active_mode)
                    # -----------------------------------------------------------------------------------------------
                    if self.deactivate_motion_capture_and_set_status_to_processing():
                        if DEBUG:
                            print('self.deactivate_motion_capture_and_set_status_to_processing(): Success!')
                        # -----------------------------------------------------------------------------------------------
                        if self.clear_change_pending_flag():
                            if DEBUG:
                                print('self.clear_change_pending_flag(): OK!')
                # -----------------------------------------------------------------------------------------------
                elif dev_active_mode == 'schedule':
                    start_time_str = dev_active_hour_start
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M:%S").time()
                    end_time_str = dev_active_hour_end
                    end_time = datetime.datetime.strptime(end_time_str, "%H:%M:%S").time()
                    current_time = datetime.datetime.now(tz).time().replace(microsecond=0)
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print("-------------------------------------------------------------------")
                        print("dev_active_mode:", dev_active_mode)
                        print("dev_active_hour_start:", dev_active_hour_start)
                        print("dev_active_hour_end:", dev_active_hour_end)
                        print("start_time_str:", start_time_str)
                        print("start_time:", start_time)
                        print("end_time_str:", end_time_str)
                        print("end_time:", end_time)
                        print("current_time:", current_time)
                        print("-------------------------------------------------------------------")
                    # -----------------------------------------------------------------------------------------------
                    # Below is a Python ternary operator (short form of if–else)
                    # current_state = 1 if self.is_time_in_range(start_time, end_time, current_time) else 0
                    # Same as below multiline code
                    if self.is_time_in_range(start_time, end_time, current_time):
                        current_state = 1
                    else:
                        current_state = 0
                    # -----------------------------------------------------------------------------------------------
                    if (current_state != previous_state) or change_pending:
                        # -----------------------------------------------------------------------------------------------
                        if current_state == 1:
                            # -----------------------------------------------------------------------------------------------
                            if self.activate_motion_capture_and_set_status_to_processing():
                                if DEBUG:
                                    print('self.activate_motion_capture_and_set_status_to_processing(): Success!')
                                # -----------------------------------------------------------------------------------------------
                                if self.clear_change_pending_flag():
                                    if DEBUG:
                                        print('self.clear_change_pending_flag(): OK!')
                        # -----------------------------------------------------------------------------------------------
                        elif current_state == 0 or change_pending:     # "or change_pending" handle runtime schedule time change
                            if self.deactivate_motion_capture_and_set_status_to_processing():
                                if DEBUG:
                                    print('self.deactivate_motion_capture_and_set_status_to_processing(): Success!')
                                # -----------------------------------------------------------------------------------------------
                                if self.clear_change_pending_flag():
                                    if DEBUG:
                                        print('self.clear_change_pending_flag(): OK!')
                        # -----------------------------------------------------------------------------------------------
                        # Update Previous State
                        previous_state = current_state
                # -----------------------------------------------------------------------------------------------
                elif dev_active_mode == 'a_on_m_off':
                    start_time_str = dev_active_hour_start
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M:%S").time()
                    # -----------------------------------------------------------------------------------------------
                    """
                    Handle the wrap-around case (e.g., if start_time = 23:00:00, then end_time = 02:00:00 next day)
                    To handle wrap-around (when end time goes past midnight), you just need to keep the time part after adding hours.
                    """
                    # Convert to datetime for adding timedelta
                    start_dt = datetime.datetime.combine(datetime.date.today(), start_time)
                    # Add 1 hours
                    end_dt = start_dt + datetime.timedelta(hours=1)
                    # Take only time part → wrap-around is handled automatically
                    end_time = end_dt.time()
                    current_time = datetime.datetime.now(tz).time().replace(microsecond=0)
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print("-------------------------------------------------------------------")
                        print("dev_active_mode:", dev_active_mode)
                        print("dev_active_hour_start:", dev_active_hour_start)
                        print("start_time_str:", start_time_str)
                        print("start_time:", start_time)
                        print("end_time:", end_time)
                        print("current_time:", current_time)
                        print("-------------------------------------------------------------------")
                    # -----------------------------------------------------------------------------------------------
                    # Below is a Python ternary operator (short form of if–else)
                    # current_state = 1 if self.is_time_in_range(start_time, end_time, current_time) else 0
                    # Same as below multiline code
                    if self.is_time_in_range(start_time, end_time, current_time):
                        current_state = 1
                    else:
                        current_state = 0
                    # -----------------------------------------------------------------------------------------------
                    if (current_state != previous_state) or change_pending:
                        # -----------------------------------------------------------------------------------------------
                        if current_state == 1:
                            # -----------------------------------------------------------------------------------------------
                            if self.activate_motion_capture_and_set_status_to_processing():
                                if DEBUG:
                                    print('self.activate_motion_capture_and_set_status_to_processing(): Success!')
                                # -----------------------------------------------------------------------------------------------
                                if self.clear_change_pending_flag():
                                    if DEBUG:
                                        print('self.clear_change_pending_flag(): OK!')
                        # -----------------------------------------------------------------------------------------------
                        # Deactivation ONLY should be Manual
                        elif current_state == 0 and change_pending:     # "or change_pending" handle runtime schedule time change
                            if self.deactivate_motion_capture_and_set_status_to_processing():
                                if DEBUG:
                                    print('self.deactivate_motion_capture_and_set_status_to_processing(): Success!')
                                # -----------------------------------------------------------------------------------------------
                                if self.clear_change_pending_flag():
                                    if DEBUG:
                                        print('self.clear_change_pending_flag(): OK!')
                        # -----------------------------------------------------------------------------------------------
                        # Update Previous State
                        previous_state = current_state
            # -----------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:DevCtrl:', e)
                break
            # ===============================================================================================


        # -----------------------------------------------------------------------------------------------
        # When while loop breaks
        self.client_socket = None
        self.address = None
        self.timeout = None
        # -----------------------------------------------------------------------------------------------
        self.data = None
        self.login_ok_flag = None
        self.dev_sl = None
        self.esp_mac = None
        self.dev_reboot_cnt = None
        self.all_motion_images_received_flag = None
        # -----------------------------------------------------------------------------------------------
        thread_counter -= 1
        if DEBUG:
            print('Thread DELETED\nTotal running thread(s):', thread_counter)
        # -----------------------------------------------------------------------------------------------
        try:
            self.client_socket.close()
        except Exception as e:
            print('e:Outside of the Thread', e)
    # ***********************************************************************************************


    # ***********************************************************************************************
    def device_login(self):
        # -----------------------------------------------------------------------------------------------
        # global thread_counter
        # -----------------------------------------------------------------------------------------------
        try:
            self.data = self.client_socket.recv(64)
            # -----------------------------------------------------------------------------------------------
            if not self.data:
                return False
            # -----------------------------------------------------------------------------------------------
            self.data = self.data.decode("utf-8")
            # print('self.data:', self.data)
            # print('self.data_len:', len(self.data))
            # -----------------------------------------------------------------------------------------------
            split_list = self.data.split(',')
            # print('split_list:', split_list)
            self.dev_sl = split_list[0].strip()
            # print('self.dev_sl:', self.dev_sl)
            self.esp_mac = split_list[1].strip()
            # print('self.esp_mac:', self.esp_mac)
            self.dev_reboot_cnt = split_list[2].strip()
            # print('self.dev_reboot_cnt:', self.dev_reboot_cnt)
            # -----------------------------------------------------------------------------------------------
            # Insert 'dev_reboot_cnt' value to DB
            self.update_reboot_counter_info()
            # -----------------------------------------------------------------------------------------------
            # Search device info in DB
            if self.search_device_info_in_db():
                if DEBUG:
                    print('Login success :)')
                # -----------------------------------------------------------------------------------------------
                self.login_ok_flag = True
                self.client_socket.send('lOgInOK\r\n'.encode())
            else:
                if DEBUG:
                    print('Incorrect login try :(\nLogin Failed :)')
                # -----------------------------------------------------------------------------------------------
                try:
                    self.client_socket.send('lOgInERR\r\n'.encode())
                    self.client_socket.close()
                except Exception as e:
                    print('e:', e)
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:Login:', e)
            # -----------------------------------------------------------------------------------------------
            try:
                self.client_socket.send('lOgInERR\r\n'.encode())
                self.client_socket.close()
            except Exception as e:
                print('e:', e)
    # ***********************************************************************************************


    # ***********************************************************************************************
    def check_device_active_status(self):
        try:
            # Always check device Active status. This will forcefully logout device without server restart
            if self.search_device_info_in_db():
                if DEBUG:
                    print('Device: ', self.dev_sl, ' is ACTIVE YES')
                # -----------------------------------------------------------------------------------------------
                return True
            else:
                if DEBUG:
                    print('Forcefully disconnecting device: ', self.dev_sl, '...')
                # -----------------------------------------------------------------------------------------------
                return False
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:Login:', e)
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def search_device_info_in_db(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT dev_sl, esp_mac_id 
            FROM app_devices_deviceinfo 
            WHERE dev_sl = ? 
            AND 
            esp_mac_id = (SELECT id FROM app_devices_espmacid WHERE esp_mac = ?) 
            AND 
            active = ? 
            LIMIT 1 
            """, (self.dev_sl, self.esp_mac, 1))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:search_device_info_in_db:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:search_device_info_in_db:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def update_hb_info(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO app_devices_deviceheartbeat
            (id, hb_time, created_at, updated_at, device_info_id_id) 
            VALUES (NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)) 
            ON CONFLICT (device_info_id_id) 
            DO UPDATE SET 
            hb_time = CURRENT_TIMESTAMP 
            WHERE device_info_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            """, (self.dev_sl, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:update_hb_info:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:update_hb_info:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def convert_mjpeg_to_mp4_and_cleanup(self, input_file, output_file):
        try:
            if not os.path.exists(input_file):
                if DEBUG:
                    print(f"File not found: {input_file}")
                # -----------------------------------------------------------------------------------------------
                return
            # -----------------------------------------------------------------------------------------------
            command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', output_file]
            # -----------------------------------------------------------------------------------------------
            try:
                if DEBUG:
                    print("Converting MJPEG to MP4...")
                # -----------------------------------------------------------------------------------------------
                # subprocess.run(command, check=True)     # Output is shown in the terminal
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # No output is shown in the terminal from the FFmpeg or any command.

                if DEBUG:
                    print(f"Conversion successful: {output_file}")
                # Delete the original MJPEG file
                # os.remove(input_file)
                # print(f"Deleted original file: {input_file}")
            # -----------------------------------------------------------------------------------------------
            except subprocess.CalledProcessError as e:
                print("Conversion failed:", e)
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:convert_mjpeg_to_mp4_and_cleanup', e)
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_snooze_value_for_this_device(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, snooze_delay = False, '', 0
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""SELECT snooze_delay FROM app_devices_deviceinfo WHERE dev_sl = ? LIMIT 1""", (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                snooze_delay = int(no_of_rows[0])
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_snooze_value_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_snooze_value_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        return snooze_delay
    # ***********************************************************************************************


    # ***********************************************************************************************
    def update_reboot_counter_info(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO app_devices_deviceheartbeat
            (id, hb_time, created_at, updated_at, device_info_id_id, no_of_reboot) 
            VALUES (NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?), ?) 
            ON CONFLICT (device_info_id_id) 
            DO UPDATE SET 
            hb_time = CURRENT_TIMESTAMP, 
            no_of_reboot = ?
            WHERE device_info_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            """, (self.dev_sl, self.dev_reboot_cnt, self.dev_reboot_cnt, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:update_reboot_counter_info:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:update_reboot_counter_info:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def insert_motion_vdo_info_to_db(self, video_size, total_frame, vdo_name, is_alert_snooze):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO 
            app_devices_motionvideofromdevice(
            insert_date_time,             
            video_size, 
            total_frame, 
            video_path, 
            is_detection_applied, 
            is_motion_found, 
            motion_found_frame_no, 
            is_person_found, 
            person_found_frame_no, 
            is_alert_done,
            is_alert_snooze,
            created_at, 
            updated_at, 
            device_info_id_id) 
            VALUES(
            CURRENT_TIMESTAMP, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP, 
            CURRENT_TIMESTAMP, 
            (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?))
            """, (video_size, total_frame, vdo_name, False, False, 0, False, 0, False, is_alert_snooze, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:insert_motion_vdo_info_to_db:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e2:
                print('e2:insert_motion_vdo_info_to_db:', e2)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_hb_delay_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, hb_delay = '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                  SELECT cmd_status, cmd_name, hb_delay 
                  FROM app_devices_hbdelaycommand 
                  WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                  LIMIT 1 
                  """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                hb_delay = no_of_rows[2]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_hb_delay_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_hb_delay_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, hb_delay
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_hb_delay(self, cmd_name, hb_delay):
        # -----------------------------------------------------------------------------------------------
        hb_delay_packet = 'hB,' + 'cHngCONFIg,' + cmd_name + ',' + str(hb_delay) + ','
        if DEBUG:
            print('hb_delay_packet:', hb_delay_packet)

        self.client_socket.send(hb_delay_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive HB Delay Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            if DEBUG:
                print('self.data:', self.data)
            # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        if DEBUG:
            print('device_reply:', device_reply)

        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_hbdelaycommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_no_of_frame_to_be_captured_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, number_of_frame = '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT cmd_status, cmd_name, number_of_frame 
            FROM app_devices_noofframetocapturecommand 
            WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            LIMIT 1 
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                number_of_frame = no_of_rows[2]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_no_of_frame_to_be_captured_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_no_of_frame_to_be_captured_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, number_of_frame
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_the_no_of_frame_to_be_captured(self, cmd_name, number_of_frame):
        # -----------------------------------------------------------------------------------------------
        frame_limit_packet = 'hB,' + cmd_name + ',' + str(number_of_frame) + ','
        self.client_socket.send(frame_limit_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive No of Frame Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            pass
            # print('self.data:', self.data)
            # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == cmd_name:
            self.restore_command_status_to_done('app_devices_noofframetocapturecommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_motion_capture_params(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size = '', '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                SELECT cmd_status, enable_or_disable_motion_capture, enable_or_disable_flash_light, no_of_frame_capture_limit, vdo_frame_size 
                FROM app_devices_controlmotioncapture 
                WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                LIMIT 1 
                """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                is_motion_capture_active = no_of_rows[1]
                is_flash_active = no_of_rows[2]
                no_of_frame_limit = no_of_rows[3]
                frame_size = no_of_rows[4]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_motion_capture_params:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_motion_capture_params:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_camera_init_params(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, cam_flip, cam_mirror = '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                    SELECT cmd_status, cmd_name, cam_flip, cam_mirror 
                    FROM app_devices_camerainitsettingcommand 
                    WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                    LIMIT 1 
                    """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                cam_flip = no_of_rows[2]
                cam_mirror = no_of_rows[3]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_camera_init_params:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_camera_init_params:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, cam_flip, cam_mirror
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_wifi_ssid_pass(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, wifi_ssid, wifi_pass = '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                        SELECT cmd_status, cmd_name, ssid, password 
                        FROM app_devices_wifissidpasscommand 
                        WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                        LIMIT 1 
                        """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                wifi_ssid = no_of_rows[2]
                wifi_pass = no_of_rows[3]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_wifi_ssid_pass:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_wifi_ssid_pass:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, wifi_ssid, wifi_pass
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_cloud_parameters(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, domain_name, ip_address, cloud_port = '', '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                        SELECT cmd_status, cmd_name, cloud_domain, cloud_ip, cloud_port 
                        FROM app_devices_cloudipdomainportcommand 
                        WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                        LIMIT 1 
                        """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                domain_name = no_of_rows[2]
                ip_address = no_of_rows[3]
                cloud_port = no_of_rows[4]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_cloud_parameters:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_cloud_parameters:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, domain_name, ip_address, cloud_port
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_device_serial_no(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, cmd_name, device_serial_no = '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                        SELECT cmd_status, cmd_name, device_sl 
                        FROM app_devices_deviceserialcommand 
                        WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                        LIMIT 1 
                        """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                cmd_name = no_of_rows[1]
                device_serial_no = no_of_rows[2]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_device_serial_no:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_device_serial_no:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, cmd_name, device_serial_no
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_light_alarm_on_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn = '', ''
        cmd_status = ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT cmd_status
            FROM app_devices_lightalarmoncommand 
            WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            AND active = ?
            LIMIT 1 
            """, (self.dev_sl, 1))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_light_alarm_on_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_light_alarm_on_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_light_alarm_off_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn = '', ''
        cmd_status = ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT cmd_status
            FROM app_devices_lightalarmoffcommand 
            WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            AND active = ?
            LIMIT 1 
            """, (self.dev_sl, 1))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_light_alarm_off_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_light_alarm_off_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_motion_capture_params(self, is_motion_capture_active, is_flash_active, no_of_frame_limit, frame_size):
        # -----------------------------------------------------------------------------------------------
        cmd_name = 'mOtioNcONf'
        motion_on_off = ''
        flash_on_off = ''
        # -----------------------------------------------------------------------------------------------
        if is_motion_capture_active:
            motion_on_off = 'MaS_On'
        else:
            motion_on_off = 'MaS_oFF'
        # -----------------------------------------------------------------------------------------------
        if is_flash_active:
            flash_on_off = 'mcf_oN'
        else:
            flash_on_off = 'mcf_OfF'
        # -----------------------------------------------------------------------------------------------
        motion_cmd_packet = 'hB,' + 'cHngCONFIg,' + cmd_name + ',' + motion_on_off + ',' + flash_on_off + ','+ str(no_of_frame_limit) + ','+ str(frame_size) + ','
        # print('motion_cmd_packet:', motion_cmd_packet)
        self.client_socket.send(motion_cmd_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive Motion Control Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            if DEBUG:
                print('self.data:', self.data)
                # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_controlmotioncapture', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_cam_init_params(self, cam_init_cmd_name, is_cam_flip, is_cam_mirror):
        # -----------------------------------------------------------------------------------------------
        cam_init_cmd_packet = 'hB,' + 'cHngCONFIg,' + cam_init_cmd_name + ',' + str(is_cam_flip) + ',' + str(is_cam_mirror) + ','
        # print('cam_init_cmd_packet:', cam_init_cmd_packet)
        self.client_socket.send(cam_init_cmd_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive Motion Control Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            pass
            # print('self.data:', self.data)
            # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_camerainitsettingcommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_wifi_ssid_password(self, ssid_pass_cmd_name, wifi_ssid, wifi_pass):
        # -----------------------------------------------------------------------------------------------
        ssid_pass_cmd_packet = 'hB,' + 'cHngCONFIg,' + ssid_pass_cmd_name + ',' + wifi_ssid + ',' + wifi_pass + ','
        # print('ssid_pass_cmd_packet:', ssid_pass_cmd_packet)
        self.client_socket.send(ssid_pass_cmd_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive Motion Control Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            if DEBUG:
                print('self.data:', self.data)
                # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_wifissidpasscommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_cloud_parameters(self, cp_cmd_name, domain_name, ip_address, cloud_port):
        # -----------------------------------------------------------------------------------------------
        cloud_param_packet = 'hB,' + 'cHngCONFIg,' + cp_cmd_name + ',' + domain_name + ',' + ip_address + ',' + str(cloud_port) + ','
        # print('cloud_param_packet:', cloud_param_packet)
        self.client_socket.send(cloud_param_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive Motion Control Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            if DEBUG:
                print('self.data:', self.data)
                # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_cloudipdomainportcommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_device_serial_no(self, devsl_cmd_name, device_serial_no):
        # -----------------------------------------------------------------------------------------------
        devsl_param_packet = 'hB,' + 'cHngCONFIg,' + devsl_cmd_name + ',' + device_serial_no + ','
        # print('devsl_param_packet:', devsl_param_packet)
        self.client_socket.send(devsl_param_packet.encode())
        # -----------------------------------------------------------------------------------------------
        # print('Blocked to receive Motion Control Reply from Device')
        self.data = self.client_socket.recv(64)
        # -----------------------------------------------------------------------------------------------
        if not self.data:
            return False
        else:
            pass
            # print('self.data:', self.data)
            # print('self.data1_len:', len(self.data))
        # -----------------------------------------------------------------------------------------------
        device_reply = self.data.decode("utf-8")
        # print('device_reply:', device_reply)
        if device_reply == 'cOnFS':
            self.restore_command_status_to_done('app_devices_deviceserialcommand', 'done')
            # -----------------------------------------------------------------------------------------------
            # Restore Device Busy to Idle mode
            if self.restore_device_busy_to_idle_mode():
                # print('CMD Restored to "Not Busy" OK')
                return True
            else:
                # print('CMD Restored to "Not Busy" FAILED')
                return False
        # -----------------------------------------------------------------------------------------------
        else:
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_light_alarm_on(self):
        try:
            light_alarm_on_packet = 'hB,' + 'cHngCONFIg,' + 'lgtAlrmChaLu' + ','
            # -----------------------------------------------------------------------------------------------
            # print(self.dev_sl, ':', 'Asking Light-Alarm ON')
            self.client_socket.send(light_alarm_on_packet.encode())
            # -----------------------------------------------------------------------------------------------
            # print('Blocked to receive Motion Control Reply from Device')
            self.data = self.client_socket.recv(64)
            # -----------------------------------------------------------------------------------------------
            if not self.data:
                return False
            else:
                if DEBUG:
                    print('self.data:', self.data)
                    # print('self.data1_len:', len(self.data))
            # -----------------------------------------------------------------------------------------------
            device_reply = self.data.decode("utf-8")
            # print('device_reply:', device_reply)
            if device_reply == 'cOnFS':
                self.restore_command_status_to_done('app_devices_lightalarmoncommand', 'done')
                self.add_to_log_light_alarm_on()
                # print('Light-Alarm ON YES')
                # -----------------------------------------------------------------------------------------------
                # Restore Device Busy to Idle mode
                if self.restore_device_busy_to_idle_mode():
                    # print('CMD Restored to "Not Busy" OK')
                    return True
                else:
                    # print('CMD Restored to "Not Busy" FAILED')
                    return False
            # -----------------------------------------------------------------------------------------------
            else:
                return False
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print(e)
            print('No Light Alarm ON Reply in  15 Sec :(')
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def add_to_log_light_alarm_on(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO app_devices_lightalarmonlog 
            (id, insert_date_time, created_at, updated_at, device_info_id_id) 
            VALUES 
            (NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)) 
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:add_to_log_light_alarm_on:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:add_to_log_light_alarm_on:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_light_alarm_off(self):
        try:
            light_alarm_off_packet = 'hB,' + 'cHngCONFIg,' + 'lgtAlrmBOnDhO' + ','
            # -----------------------------------------------------------------------------------------------
            # print(self.dev_sl, ':', 'Asking Light-Alarm OFF')
            self.client_socket.send(light_alarm_off_packet.encode())
            # -----------------------------------------------------------------------------------------------
            self.data = self.client_socket.recv(64)
            # -----------------------------------------------------------------------------------------------
            if not self.data:
                return False
            else:
                if DEBUG:
                    print('self.data:', self.data)
                    # print('self.data1_len:', len(self.data))
            # -----------------------------------------------------------------------------------------------
            device_reply = self.data.decode("utf-8")
            # print('device_reply:', device_reply)
            if device_reply == 'cOnFS':
                self.restore_command_status_to_done('app_devices_lightalarmoffcommand', 'done')
                self.add_to_log_light_alarm_off()
                # print('Light-Alarm OFF YES')
                # -----------------------------------------------------------------------------------------------
                # Restore Device Busy to Idle mode
                if self.restore_device_busy_to_idle_mode():
                    # print('CMD Restored to "Not Busy" OK')
                    return True
                else:
                    # print('CMD Restored to "Not Busy" FAILED')
                    return False
            # -----------------------------------------------------------------------------------------------
            else:
                return False
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print(e)
            print('No Light Alarm OFF Reply in  15 Sec :(')
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def add_to_log_light_alarm_off(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO app_devices_lightalarmofflog 
            (id, insert_date_time, created_at, updated_at, device_info_id_id) 
            VALUES 
            (NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)) 
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:add_to_log_light_alarm_off:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:add_to_log_light_alarm_off:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_manual_image_capture_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status, flashlight, resolution, resolution_visual = '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT cmd_status, flashlight, cmd, cmd_visual
            FROM app_devices_imagecapturecommand 
            INNER JOIN app_devices_imageresolutionlist
            ON 
            app_devices_imagecapturecommand.resolution_id = app_devices_imageresolutionlist.id
            WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            LIMIT 1 
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status = no_of_rows[0]
                flashlight = no_of_rows[1]
                resolution = no_of_rows[2]
                resolution_visual = no_of_rows[3]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_cmd_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status, flashlight, resolution, resolution_visual
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_reboot_cnt_reset_cmd(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        cmd_status_rc, cmd_name = '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT cmd_status, cmd_name 
            FROM app_devices_resetrebootcountercommand 
            WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            LIMIT 1 
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                cmd_status_rc = no_of_rows[0]
                cmd_name = no_of_rows[1]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_reboot_cnt_reset_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_reboot_cnt_reset_cmd:', e)
        # -----------------------------------------------------------------------------------------------
        return cmd_status_rc, cmd_name
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_reboot_cnt_reset_cmd(self, cmd_name_rc):
        try:
            reboot_reset_packet = 'hB,' + 'cHngCONFIg,' + cmd_name_rc + ','
            # -----------------------------------------------------------------------------------------------
            self.client_socket.send(reboot_reset_packet.encode())
            # -----------------------------------------------------------------------------------------------
            self.data = self.client_socket.recv(64)
            # -----------------------------------------------------------------------------------------------
            if not self.data:
                return False
            else:
                if DEBUG:
                    print('self.data:', self.data)
                    # print('self.data1_len:', len(self.data))
            # -----------------------------------------------------------------------------------------------
            device_reply = self.data.decode("utf-8")
            # print('device_reply:', device_reply)
            if device_reply == 'cOnFS':
                self.restore_command_status_to_done('app_devices_resetrebootcountercommand', 'done')
                self.set_reboot_counter_to_zero_in_hb_table()
                # -----------------------------------------------------------------------------------------------
                # Restore Device Busy to Idle mode
                if self.restore_device_busy_to_idle_mode():
                    # print('CMD Restored to "Not Busy" OK')
                    return True
                else:
                    # print('CMD Restored to "Not Busy" FAILED')
                    return False
            # -----------------------------------------------------------------------------------------------
            else:
                return False
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:set_reboot_cnt_reset_cmd:', e)
            return False
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_reboot_counter_to_zero_in_hb_table(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            UPDATE app_devices_deviceheartbeat 
            SET no_of_reboot = ?
            WHERE device_info_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            """, (0, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:set_reboot_counter_to_zero_in_hb_table:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:set_reboot_counter_to_zero_in_hb_table:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_ts_from_last_unsnoozed_file_name(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, last_captured_file_name = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT video_path 
            FROM app_devices_motionvideofromdevice 
            WHERE 
            device_info_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?) AND 
            is_alert_snooze = FALSE 
            ORDER BY id DESC 
            LIMIT 1
            """, (self.dev_sl,))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                last_captured_file_name = no_of_rows[0]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_snooze_value_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_snooze_value_for_this_device:', e)
        # -----------------------------------------------------------------------------------------------
        return last_captured_file_name
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_motion_mode_and_active_schedule(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn = '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT dev_active_mode, dev_active_hour_start, dev_active_hour_end, change_pending 
            FROM app_devices_deviceinfo 
            WHERE dev_sl = ? 
            AND active = ? 
            LIMIT 1 
            """, (self.dev_sl, 1))
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                return no_of_rows[0], no_of_rows[1], no_of_rows[2], no_of_rows[3]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_motion_mode_and_active_schedule:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_motion_mode_and_active_schedule:', e)
        # -----------------------------------------------------------------------------------------------
        return '', '', '', ''
    # ***********************************************************************************************


    # ***********************************************************************************************
    def activate_motion_capture_and_set_status_to_processing(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            # -----------------------------------------------------------------------------------------------
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            UPDATE app_devices_controlmotioncapture 
            SET 
            enable_or_disable_motion_capture = ?, 
            cmd_status = ? 
            WHERE 
            device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
            """, (True, 'processing', self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:activate_motion_capture_and_set_status_to_processing():', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:activate_motion_capture_and_set_status_to_processing():', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def deactivate_motion_capture_and_set_status_to_processing(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            # -----------------------------------------------------------------------------------------------
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                UPDATE app_devices_controlmotioncapture 
                SET 
                enable_or_disable_motion_capture = ?, 
                cmd_status = ? 
                WHERE 
                device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)
                """, (False, 'processing', self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:deactivate_motion_capture_and_set_status_to_processing():', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:deactivate_motion_capture_and_set_status_to_processing():', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def clear_change_pending_flag(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            # -----------------------------------------------------------------------------------------------
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            UPDATE app_devices_deviceinfo 
            SET 
            change_pending = ? 
            WHERE 
            dev_sl = ?
            """, (False, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:clear_change_pending_flag:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:clear_change_pending_flag:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def is_time_in_range(self, start: time, end: time, now: time) -> bool:
        """
        Check if current time is within the range.
        Works for both normal and overnight ranges.
        ব্যাখ্যা:
        is_time_in_range() ফাংশন detect করবে রেঞ্জ দিনের ভেতরে নাকি overnight।
        উদাহরণ:
        06:00 → 21:00 → দিনের ভেতরে range।
        22:00 → 06:00 → overnight range।
        x কেবল তখনই আপডেট হবে যখন state পরিবর্তন হবে।
        """
        if start <= end:
            # Normal range (e.g. 06:00 → 21:00)
            return start <= now <= end
        else:
            # Overnight range (e.g. 22:00 → 06:00 next day)
            return now >= start or now <= end
    # ***********************************************************************************************


    # ***********************************************************************************************
    def set_manual_image_capture(self, flashlight, resolution):
        try:
            # print(self.dev_sl, ':', 'Asking for Photo...')
            # Below Values Read from DB
            cmd_cap = 'cApPiC,'
            resolution = str(resolution) + ','
            quality = '10,'
            extra_flash = str(flashlight) + ','
            # -----------------------------------------------------------------------------------------------
            command_for_client = 'hB,' + 'cHngCONFIg,' + cmd_cap + resolution + quality + extra_flash
            self.client_socket.send(command_for_client.encode())
            # -----------------------------------------------------------------------------------------------
            self.data = self.client_socket.recv(64)
            # -----------------------------------------------------------------------------------------------
            if not self.data:
                return False
            # -----------------------------------------------------------------------------------------------
            # Extract Image Length
            img_len_with_marker = self.data.decode().strip()
            if DEBUG:
                print('img_len_with_marker:', img_len_with_marker)

            if img_len_with_marker.startswith("imglen,"):
                # Extract size as integer
                img_size = int(img_len_with_marker.split(",")[1])
                if DEBUG:
                    print("Image size_Int:", img_size)
                # -----------------------------------------------------------------------------------------------
                img_buffer = b""
                if DEBUG:
                    print('Echo back:', self.data)
                self.client_socket.send(self.data)
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('Loop until (FULL Image) ', img_size, 'bytes received...')
                # -----------------------------------------------------------------------------------------------
                while len(img_buffer) < img_size:
                    packet = self.client_socket.recv(4096)
                    if DEBUG:
                        print('Packet Received byte --->:', len(packet))
                    # -----------------------------------------------------------------------------------------------
                    if not packet:
                        return False
                    # -----------------------------------------------------------------------------------------------
                    img_buffer += packet
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print("An image FULLY received. Size (bytes):", len(img_buffer))
                # Save image to file
                # Receive images Here. Create file name and path
                ts = str(int(time.time()))
                # -----------------------------------------------------------------------------------------------
                manual_captured_path = img_file_path + str(self.dev_sl) + '/manual_captured'
                os.makedirs(manual_captured_path, exist_ok=True)
                manual_captured_file_name = open(f"{manual_captured_path}/{ts}.jpeg", "wb")
                # -----------------------------------------------------------------------------------------------
                manual_captured_file_name.write(img_buffer)
                manual_captured_file_name.write(bytes([0xFF, 0xD9]))  # End of JPEG marker
                # -----------------------------------------------------------------------------------------------
                # Check if file exists
                captured_file_name = img_file_path + str(self.dev_sl) + '/manual_captured/' + ts + '.jpeg'

                if os.path.isfile(captured_file_name):
                    # Check file size
                    image_size = os.path.getsize(captured_file_name)

                    if image_size == 0:
                        os.remove(captured_file_name)
                        if DEBUG:
                            print(f"{captured_file_name} was 0 KB and has been DELETED.")
                    # -----------------------------------------------------------------------------------------------
                    else:
                        if DEBUG:
                            print(f"{captured_file_name} is NOT 0 Size.")
                        # -----------------------------------------------------------------------------------------------
                        # Calculate Image Size again after Detection (Normally Size Increased)
                        image_size = os.path.getsize(captured_file_name)
                        # print('img_size:', image_size)
                        captured_file_name_for_db = str(self.dev_sl) + '/manual_captured/' + ts + '.jpeg'

                        if self.insert_manually_captured_image_info_to_db(image_size, captured_file_name_for_db):
                            if DEBUG:
                                print('Image info saved in DB success!')
                        else:
                            if DEBUG:
                                print('Image info saved in DB FAILED!')
                        # -----------------------------------------------------------------------------------------------
                        self.restore_command_status_to_done('app_devices_imagecapturecommand', 'done')
                        # -----------------------------------------------------------------------------------------------
                        # Restore Device Busy to Idle mode
                        if self.restore_device_busy_to_idle_mode():
                            if DEBUG:
                                print('CMD Restored to "Not Busy" OK')
                        else:
                            if DEBUG:
                                print('Restore to "Not Busy" NO!')
                # -----------------------------------------------------------------------------------------------
                else:
                    if DEBUG:
                        print("Manually Captured file does not exist.")
                # -----------------------------------------------------------------------------------------------
                self.data = ''
                captured_file_name = ''
                if DEBUG:
                    print("Confirming Client...")
                self.client_socket.send("sImgRcvd".encode())
                # -----------------------------------------------------------------------------------------------
                return True
            # -----------------------------------------------------------------------------------------------
            else:
                return False
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:set_manual_image_capture: ', e)
            return False
        # -----------------------------------------------------------------------------------------------
    # ***********************************************************************************************


    # ***********************************************************************************************
    def insert_manually_captured_image_info_to_db(self, image_size, image_path):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            INSERT INTO 
            app_devices_manualcapturedimage(
            insert_date_time, 
            created_at, 
            updated_at, 
            device_info_id_id, 
            image_size, 
            image_path) 
            VALUES(
            CURRENT_TIMESTAMP, 
            CURRENT_TIMESTAMP, 
            CURRENT_TIMESTAMP, 
            (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?), 
            ?, ?)
            """, (self.dev_sl, image_size, image_path))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:insert_manually_captured_image_info_to_db:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e2:
                print('e2:insert_manually_captured_image_info_to_db:', e2)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # SOME COMMON FUNCTIONS START .......
    # ***********************************************************************************************
    def restore_command_status_to_done(self, table_name, status):
        # -----------------------------------------------------------------------------------------------
        # Validate table name (alphanumeric + underscores only)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError("Invalid table name!")
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = '', '', False
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            query = f"""UPDATE {table_name} SET cmd_status = ? WHERE device_id_id = (SELECT id FROM app_devices_deviceinfo WHERE dev_sl = ?)"""
            cur.execute(query, (status, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
            if DEBUG:
                print(f"Status updated to 'done' in table '{table_name}' for device: {self.dev_sl}")
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:restore_command_status_to_done:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:restore_command_status_to_done:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


    # ***********************************************************************************************
    def restore_device_busy_to_idle_mode(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = '', '', False
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            UPDATE app_devices_deviceinfo 
            SET 
            busy_status = ? 
            WHERE 
            dev_sl = ?
            """, (0, self.dev_sl))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:restore_device_busy_to_idle_mode:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:restore_device_busy_to_idle_mode:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************
# ***********************************************************************************************


# ***********************************************************************************************
def start_program():
    try:
        # global thread_counter
        # -----------------------------------------------------------------------------------------------
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST_IP, HOST_PORT))
            server_socket.listen(33)
            # -----------------------------------------------------------------------------------------------
            if DEBUG:
                print('Socket created success!')
                print('Socket has been bounded successfully!')
                print('Socket listening has been started...')
                print('Waiting for client connection...')
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e:socket_create_bind_listen:', e)
            sys.exit()
        # -----------------------------------------------------------------------------------------------
        while True:
            try:
                client_socket, address = server_socket.accept()
                # -----------------------------------------------------------------------------------------------
                if DEBUG:
                    print('Connection Details:', address)
                    print('Connected Client: ' + address[0] + ':' + str(address[1]))
                # -----------------------------------------------------------------------------------------------
                timeout = client_socket.settimeout(DEFAULT_TIMEOUT)
                client_thread = ClientThread(client_socket, address, timeout)
                client_thread.start()
                client_thread_list.append(client_thread)
                # thread_counter += 1
                # print('Total running thread(s): ', thread_counter)
            except Exception as e:
                print(e)
                continue
        # -----------------------------------------------------------------------------------------------
        # When server ends gracefully (through user keyboard interrupt), wait until remaining threads finish
        for item in client_thread_list:
            item.join()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e:start_program():', e)
# ***********************************************************************************************
