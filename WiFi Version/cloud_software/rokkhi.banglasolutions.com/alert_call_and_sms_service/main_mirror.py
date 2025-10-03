#!/usr/bin/python3
# -----------------------------------------------------------------------------------------------
from time import gmtime, strftime
from datetime import datetime, timedelta
from threading import Lock, Thread
import pathlib
from pathlib import Path
import threading
import binascii
import datetime
import socket
import select
import struct  # for packing/unpacking binary data
import glob
import sqlite3
# from socket import socket, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, AF_INET
import requests
import shutil
import time
import sys
from time import sleep
# from ultralytics import YOLO
# import cv2
import sqlite3
import re
# import numpy as np
import os
import subprocess
# -----------------------------------------------------------------------------------------------
# import db_mgnt_sql3
# -----------------------------------------------------------------------------------------------
db_path = '/home/just/rokkhi.banglasolutions.com/client_software/proj_rokkhi_banglasolutions_com_db.sqlite3'
# -----------------------------------------------------------------------------------------------
HOST_IP = 'rokkhi.banglasolutions.com'
HOST_PORT = 9473
thread_counter = 0
# Create a list in which threads will be stored in order to be joined later
client_thread_list = []
DEFAULT_TIMEOUT = 300
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
class ClientThread(Thread):
    # ***********************************************************************************************
    def __init__(self, client_socket, address, timeout):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.timeout = timeout
        self.data = None
    # ***********************************************************************************************

    # ***********************************************************************************************
    def run(self):
        global thread_counter
        # -----------------------------------------------------------------------------------------------
        thread_counter += 1
        print('New Device Connected!\nNew Thread CREATED\nTotal running thread(s): ', thread_counter)
        # -----------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------
        # Infinite Loop
        while True:
            try:
                # ===============================================================================================
                self.data = self.client_socket.recv(256)
                print('self.data RAW:', self.data)
                # -----------------------------------------------------------------------------------------------
                if not self.data:
                    print('No data received TIMEOUT!!')
                # -----------------------------------------------------------------------------------------------
                else:
                    self.data = self.data.decode().strip()
                    print('self.data STRIPPED:', self.data)
                # ===============================================================================================


                # ===============================================================================================
                if self.data == 'hB':
                    print('HB received from Calling Device!\nNO Need to Update Just EcoBack')
                    self.client_socket.send(self.data.encode())
                # -----------------------------------------------------------------------------------------------
                elif self.data == 'gIveAlRTdatA':
                    print('"Calling Device" asked for PENDING Alert Data!')
                    # -----------------------------------------------------------------------------------------------


                    # -----------------------------------------------------------------------------------------------
                    alert_row_id, dev_sl, dev_name, dev_alert_type, alert_number, alert_email = self.read_alert_call_parameters()
                    print('alert_row_id, dev_sl, dev_name, dev_alert_type, alert_number, alert_email:', alert_row_id, dev_sl, dev_name, dev_alert_type, alert_number, alert_email)

                    if alert_row_id and dev_sl and dev_name and dev_alert_type and alert_number:
                        reply_packet = f"{self.data}-{alert_row_id}-{dev_sl}-{dev_name}-{dev_alert_type}-{alert_number}-{alert_email}"
                        print('reply_packet:', reply_packet)
                        # -----------------------------------------------------------------------------------------------
                        self.client_socket.send(reply_packet.encode())
                    # -----------------------------------------------------------------------------------------------
                    else:
                        reply_packet = f"{self.data}-NO_PENDING-{dev_sl}-{dev_name}-{dev_alert_type}-{alert_number}-{alert_email}"
                        print('reply_packet:', reply_packet)
                        self.client_socket.send(reply_packet.encode())
                # -----------------------------------------------------------------------------------------------
                elif 'caLLdOnE' in self.data:
                    print('Alert Call Status Updating...')
                    reply_buff_list = self.data.split(",")
                    row_id_done = reply_buff_list[1]
                    print('row_id_done:', row_id_done)
                    # -----------------------------------------------------------------------------------------------
                    if self.update_alert_status(row_id_done):
                        print('Alert Call Status Update Success :)\nInforming Client...')
                        self.client_socket.send(self.data.encode())
                    else:
                        print('Alert Call Status Update FAILED!')
            # ===============================================================================================
            except Exception as e:
                print('e:Exception in Main While Loop', e)
    # ***********************************************************************************************


    # ***********************************************************************************************
    def read_alert_call_parameters(self):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        alert_row_id, dev_sl, dev_name, dev_alert_type, alert_number, alert_email = '', '', '', '', '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
            SELECT 
            m.id AS alert_row_id,
            d.dev_sl,
            d.dev_name,
            d.dev_alert_type,
            d.alert_number,
            d.alert_email
            FROM 
            app_devices_motionvideofromdevice AS m
            INNER JOIN 
            app_devices_deviceinfo AS d
            ON 
            m.device_info_id_id = d.id
            WHERE 
            m.is_detection_applied = TRUE 
            AND m.is_person_found = TRUE 
            AND m.is_alert_done = FALSE
            AND m.is_alert_snooze = FALSE
            ORDER BY m.id ASC
            LIMIT 1;
            """)
            # -----------------------------------------------------------------------------------------------
            no_of_rows = cur.fetchone()
            # print('no_of_rows:', no_of_rows)
            # -----------------------------------------------------------------------------------------------
            if no_of_rows:
                alert_row_id = no_of_rows[0]
                dev_sl = no_of_rows[1]
                dev_name = no_of_rows[2]
                dev_alert_type = no_of_rows[3]
                alert_number = no_of_rows[4]
                alert_email = no_of_rows[5]
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:read_alert_call_parameters:', e)
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:read_alert_call_parameters:', e)
        # -----------------------------------------------------------------------------------------------
        return alert_row_id, dev_sl, dev_name, dev_alert_type, alert_number, alert_email
    # ***********************************************************************************************


    # ***********************************************************************************************
    def update_alert_status(self, row_id_done):
        # -----------------------------------------------------------------------------------------------
        cur, conn, result = False, '', ''
        # -----------------------------------------------------------------------------------------------
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # -----------------------------------------------------------------------------------------------
            cur.execute("""
                UPDATE app_devices_motionvideofromdevice 
                SET 
                is_alert_done = ? 
                WHERE 
                id = ? 
                """, (True, row_id_done))
            # -----------------------------------------------------------------------------------------------
            conn.commit()
            result = True
        # -----------------------------------------------------------------------------------------------
        except Exception as e:
            print('e1:update_alert_status:', e)
            conn.rollback()
        # -----------------------------------------------------------------------------------------------
        finally:
            try:
                cur.close()
                conn.close()
            except Exception as e:
                print('e2:update_alert_status:', e)
        # -----------------------------------------------------------------------------------------------
        return result
    # ***********************************************************************************************


# ***********************************************************************************************
def start_program():
    try:
        # global thread_counter
        # -----------------------------------------------------------------------------------------------
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('Socket created success!')
            # -----------------------------------------------------------------------------------------------
            server_socket.bind((HOST_IP, HOST_PORT))
            print('Socket has been bounded successfully!')
            # -----------------------------------------------------------------------------------------------
            server_socket.listen(33)
            print('Socket listening has been started...')
            print('Waiting for client connection...')
        except Exception as e:
            print('e:socket_create_bind_listen:', e)
            sys.exit()
        # -----------------------------------------------------------------------------------------------
        while True:
            try:
                client_socket, address = server_socket.accept()
                # print('Connection Details:', address)
                print('Connected Client: ' + address[0] + ':' + str(address[1]))
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


