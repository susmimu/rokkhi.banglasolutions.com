# -----------------------------------------------------------------------------------------------
from time import sleep
from machine import Pin
import uart_mgnt
import os
import machine
# -----------------------------------------------------------------------------------------------
PROTOCOL = 'TCP'
# SERVER_DOMAIN = 'www.eagleeye.lalsobujtech.com'
SERVER_DOMAIN = '128.199.154.33'
# SERVER_IP = '128.199.154.33'
SERVER_PORT = '9473'
APN, OP_NAME, CELL_NO = '', '', ''
# -----------------------------------------------------------------------------------------------
modem_imei = ''
sim_uniq_id = ''
# -----------------------------------------------------------------------------------------------
DEBUG_MODEM = True
DEBUG_AT = False
DEBUG_NETWORK = True
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
modem_rst_pin = Pin(4, Pin.OUT)     # create output pin on GPIO15
modem_rst_pin.on()                  # set pin to "on" (high) level
# modem_rst_pin.off()               # set pin to "off" (low) level
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def restart_modem():
    try:
        modem_rst_pin.off()
        sleep(1)
        modem_rst_pin.on()
        # sleep(1)
        if DEBUG_MODEM:
            print('Modem restart success :)')
    except Exception as e:
        print('restart_modem:e:', e)
# ***********************************************************************************************


# ***********************************************************************************************
def at_command_executive(cmd, expected_reply):
    # -----------------------------------------------------------------------------------------------
    buffer = ''
    cmd += '\r\n'
    wait_counter = 0
    # -----------------------------------------------------------------------------------------------
    if DEBUG_AT:
        print('cmd >>>:', cmd)
        print('expected_reply <<<:', expected_reply)
    # -----------------------------------------------------------------------------------------------
    try:
        # If Need to Write AT Command OR Auto Come in Modem UART after Reset
        if cmd:
            uart_mgnt.uart2.write(cmd)
        # -----------------------------------------------------------------------------------------------
        while True:
            # -----------------------------------------------------------------------------------------------
            reply_byte = uart_mgnt.uart2.read(1)

            if DEBUG_AT:
                print('reply_byte:', reply_byte)
            # -----------------------------------------------------------------------------------------------

            # -----------------------------------------------------------------------------------------------
            if not reply_byte:
                if DEBUG_AT:
                    print("b'' or None Received from modem :(\nRebooting...")

                machine.reset()
            # -----------------------------------------------------------------------------------------------
            else:
                try:
                    reply_byte_decoded = reply_byte.decode("utf-8")

                    if DEBUG_AT:
                        print('reply_byte_decoded:', reply_byte_decoded)
                    # -----------------------------------------------------------------------------------------------
                    if 31 < ord(reply_byte_decoded) < 128:
                        buffer += reply_byte_decoded

                        if DEBUG_AT:
                            print('buffer:', buffer)
                except Exception as e:
                    if DEBUG_AT:
                        print('e:', e)
                        print('Non "utf-8" byte received :(')
            # -----------------------------------------------------------------------------------------------

            # -----------------------------------------------------------------------------------------------
            if expected_reply in buffer:
                if DEBUG_AT:
                    print(f'buffer: {buffer}')
                    print('Correct AT-Reply received from modem :)')
                # -----------------------------------------------------------------------------------------------
                if cmd == 'AT+GSN\r\n' or cmd == 'AT+CCID\r\n':
                    return cmd, buffer
                else:
                    return True
            # -----------------------------------------------------------------------------------------------
            else:
                # If "utf-8" characters receiving but not matching with expected reply. 1ms wait
                wait_counter += 1
                sleep(0.001)    # 1 ms Delay

                if wait_counter > 30000:
                    if DEBUG_AT:
                        print('30 Sec waiting done!\nRebooting...')

                    machine.reset()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_AT:
            print('e:', e)
            print('at_command_executive():\nRebooting...')

        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def network_ready():
    global modem_imei, sim_uniq_id
    # -----------------------------------------------------------------------------------------------
    try:
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('', 'Call Ready'):
            if DEBUG_NETWORK:
                print('Call Ready Found :)')
        else:
            if DEBUG_NETWORK:
                print('Call Ready NOT Found!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('ATE0&W', 'OK'):
            if DEBUG_NETWORK:
                print('Echo off success :)')
        else:
            if DEBUG_NETWORK:
                print('Echo off FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+IPR=115200', 'OK'):
            if DEBUG_NETWORK:
                print('Baud Rate set success :)')
        else:
            if DEBUG_NETWORK:
                print('Baud Rate set FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT', 'OK'):
            if DEBUG_NETWORK:
                print('Echo off check success :)')
        else:
            if DEBUG_NETWORK:
                print('Echo off check FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CREG?', 'OK'):
            if DEBUG_NETWORK:
                print('Network registration status check OK :)')
        else:
            if DEBUG_NETWORK:
                print('Network registration status check FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CMGF=1', 'OK'):
            if DEBUG_NETWORK:
                print('SMS format to TXT mode set Success :)')
        else:
            if DEBUG_NETWORK:
                print('SMS format to TXT mode set FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CMGD=1,4', 'OK'):
            if DEBUG_NETWORK:
                print('All SMS Delete Success :)')
        else:
            if DEBUG_NETWORK:
                print('All SMS Delete FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CNMI=0,0,0,0,0', 'OK'):
            if DEBUG_NETWORK:
                print('Turns SMS notification OFF Success :)')
        else:
            if DEBUG_NETWORK:
                print('Turns SMS notification OFF FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        # if at_command_executive('AT+GSMBUSY=1', 'OK'):
        #     if DEBUG_NETWORK:
        #         print('Reject Incoming Call ENABLE Success :)')
        # else:
        #     if DEBUG_NETWORK:
        #         print('Reject Incoming Call ENABLE FAILED!\nRebooting...')
        #
        #     machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CWHITELIST=1,1,+8801618354444', 'OK'):
            if DEBUG_NETWORK:
                print('Acceptable Call White List ENABLE Success :)')
        else:
            if DEBUG_NETWORK:
                print('Acceptable Call White List ENABLE FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        # if at_command_executive('ATD*566#;', 'OK'):
        #     if DEBUG_NETWORK:
        #         print('Balance check Success :)')
        # else:
        #     if DEBUG_NETWORK:
        #         print('Balance check FAILED!\nRebooting...')
        #
        #     machine.reset()
        # -----------------------------------------------------------------------------------------------
        cmd, buffer = at_command_executive('AT+GSN', 'OK')

        # if DEBUG_NETWORK:
        #     print(f'cmd: {cmd}, buffer: {buffer}')

        modem_imei = buffer[:-2]

        if DEBUG_NETWORK:
            print('modem_imei:', modem_imei)
        # -----------------------------------------------------------------------------------------------
        if cmd and buffer:
            if DEBUG_NETWORK:
                print('IMEI read success :)')
        else:
            if DEBUG_NETWORK:
                print('IMEI read FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        cmd, buffer = at_command_executive('AT+CCID', 'OK')

        # if DEBUG_NETWORK:
        #     print(f'cmd: {cmd}, buffer: {buffer}')

        sim_uniq_id = buffer[:-2]

        if DEBUG_NETWORK:
            print('sim_uniq_id:', sim_uniq_id)
        # -----------------------------------------------------------------------------------------------
        if cmd and buffer:
            if DEBUG_NETWORK:
                print('CCID read success :)')
        else:
            if DEBUG_NETWORK:
                print('CCID read FAILED!\nRebooting...')

            machine.reset()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_NETWORK:
            print('e:', e)
            print('network_ready() FAILED!\nRebooting...')

        machine.reset()
    # -----------------------------------------------------------------------------------------------
    return True
# ***********************************************************************************************


# ***********************************************************************************************
def call_to_a_mobile_no(cell_no):
    try:
        call_pkt = f"ATD{cell_no};\r\n"
        # -----------------------------------------------------------------------------------------------
        uart_mgnt.write_to_uart2(call_pkt)

        if DEBUG_NETWORK:
            print('Call Started...')
        # -----------------------------------------------------------------------------------------------
        sleep(25)
        uart_mgnt.write_to_uart2("ATH\r\n")

        if DEBUG_NETWORK:
            print('Call Ended...')
        # sleep(5)
    except Exception as e:
        if DEBUG_AT:
            print('e:call_to_a_mobile_no:', e)
# ***********************************************************************************************





# ***********************************************************************************************
def gprs_ready():
    try:
        # -----------------------------------------------------------------------------------------------
        gprs_ready_flag = True
        global PROTOCOL, SERVER_DOMAIN, SERVER_IP, SERVER_PORT
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CIPSHUT', 'SHUT OK'):
            if DEBUG_MODEM:
                print('GPRS PDP Context deactivate success :)')
        else:
            if DEBUG_MODEM:
                print('GPRS PDP Context deactivate FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CGATT=0', 'OK'):
            if DEBUG_MODEM:
                print('Detached from GPRS service success :)')
        else:
            if DEBUG_MODEM:
                print('Detached from GPRS service FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CGATT?', 'OK'):
            if DEBUG_MODEM:
                print('Modem is registered to GPRS :)')
        else:
            if DEBUG_MODEM:
                print('Modem is registered to GPRS FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CSTT="","",""', 'OK'):
            if DEBUG_MODEM:
                print('APN, Username, Password set success :)')
        else:
            if DEBUG_MODEM:
                print('APN, Username, Password set FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CIICR', 'OK'):
            if DEBUG_MODEM:
                print('Wireless connection with GPRS success :)')
        else:
            if DEBUG_MODEM:
                print('Wireless connection with GPRS FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CIFSR', '.'):
            if DEBUG_MODEM:
                print('Got Local IP address success :)')
        else:
            if DEBUG_MODEM:
                print('Got Local IP address FAILED!\nRebooting...')

            machine.reset()
        # -----------------------------------------------------------------------------------------------
        if at_command_executive('AT+CIPSTART="' + PROTOCOL + '","' + SERVER_DOMAIN + '","' + SERVER_PORT + '"','CONNECT OK'):
        # if at_command_executive('AT+CIPSTART="' + PROTOCOL + '","' + SERVER_IP + '","' + SERVER_PORT + '"', 'CONNECT OK', 1000, 1):
            if DEBUG_MODEM:
                print('TCP connection start success :)')
        else:
            if DEBUG_MODEM:
                print('TCP connection start FAILED!\nRebooting...')

            machine.reset()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        if DEBUG_MODEM:
            print('e:gprs_ready():', e)
            print('gprs_ready():FAILED!\nRebooting...')

        machine.reset()
    # -----------------------------------------------------------------------------------------------
    return True
# ***********************************************************************************************


# ***********************************************************************************************
def send_reply_to_server(packet):
    # -----------------------------------------------------------------------------------------------
    success_flag = True
    data_len = str(len(packet))
    # -----------------------------------------------------------------------------------------------
    if at_command_executive('AT+CIPSEND=' + data_len, '>', 10000, 1):
        # print('Modem ready to put data :)')
        pass
    else:
        # print('Modem NOT ready to put data :(')
        success_flag = False
    # -----------------------------------------------------------------------------------------------
    if success_flag:
        try:
            uart_mgnt.uart2.write(packet)
            reply_hb_packet = uart_mgnt.uart2.readline()
            reply_hb_packet = uart_mgnt.uart2.readline()
            # print('reply_hb_packet........:', reply_hb_packet)
            # print('reply_hb_packet_len.........:', len(reply_hb_packet))            
            # reply_hb_packet_decoded = reply_hb_packet.decode("utf-8")
            # print('reply_hb_packet_decoded:', reply_hb_packet_decoded)
            # print('reply_hb_packet_decoded_len.........:', len(zeply_hb_packet_decoded))
            # -----------------------------------------------------------------------------------------------
            if b'SEND OK\r\n' in reply_hb_packet:
                # print('"' + str(packet) + '" Sent to server OK :)')
                pass
            else:
                machine.reset()
        # -----------------------------------------------------------------------------------------------            
        except Exception as e:
            print('e:', e)
            print('UART Timeout :(')
            machine.reset()
    # -----------------------------------------------------------------------------------------------
    return success_flag
# ***********************************************************************************************


# ***********************************************************************************************
def send_photo_to_server():
    try:
        f = open('/photo.JPEG', 'rb')
        buffer = ''
        send_counter = 0
        # -----------------------------------------------------------------------------------------------
        while True:
            send_counter += 1
            print('send_counter:', send_counter)
            # Send Data Through TCP
            buffer = f.read(1024)
            # print('buffer:', buffer)
            # -----------------------------------------------------------------------------------------------
            if not buffer:
                break
            # -----------------------------------------------------------------------------------------------
            b_len = len(buffer)
            # print('Buffer Length:', b_len)
            # -----------------------------------------------------------------------------------------------
            if not at_command_executive('AT+CIPSEND=' + str(b_len), '>', 30000, 1):
                print('Modem failed to ready for put data :(')
                machine.reset()
            # -----------------------------------------------------------------------------------------------
            try:
                # Put data stream to be sent (Max 1024 bytes)                
                uart_mgnt.uart2.write(buffer)
                reply_byte = uart_mgnt.uart2.read(12)
                # reply_byte = uart_mgnt.uart2.read(12).decode("utf-8")                
                # print('reply_byte:', reply_byte)
                # print('reply_byte_len:', len(reply_byte))
                
                if reply_byte != b' \r\nSEND OK\r\n':
                    print('"SEND OK" not found :(')
                    machine.reset()
            except Exception as e:
                print('e123:', e)
                print('UART Timeout :(')
                machine.reset()
        # -----------------------------------------------------------------------------------------------
        f.close()
        print('Image transfer to server done :)')
        # -----------------------------------------------------------------------------------------------
        # Delete old file if any and freeup memory
        try:
            os.remove('/photo.JPEG')
        except Exception as e:
            print('e:', e)
            print('os.remove FAILED')
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e234:', e)
        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def send_sms(sms_send_to, mac):
    sms_sent_flag = False
    cmd_status = True
    
    try:
        # -----------------------------------------------------------------------------------------------
        if cmd_status:
            if at_command_executive('AT+CMGF=1', 'OK'):
                # print('SMS Text mode set :)')
                pass
            else:
                cmd_status = False
        # -----------------------------------------------------------------------------------------------
        if cmd_status:
            if at_command_executive('AT+CMGS="' + sms_send_to + '"\r', '>'):
                # print('> Found :)')
                pass
            else:
                cmd_status = False
        # -----------------------------------------------------------------------------------------------
        if cmd_status:
            CTRLZ = b'\x1A'
            
            # uart_mgnt.uart2.write('\n')
            uart_mgnt.uart2.write('MAC: ' + mac)
            uart_mgnt.uart2.write(CTRLZ)
            
            if at_command_executive('', '+CMGS:'):
                #print('SMS sent success :)')
                sms_sent_flag = True
            else:
                print('SMS send FAILED!')
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('Exception: send_sms():', e)
    # -----------------------------------------------------------------------------------------------
    return sms_sent_flag
# ***********************************************************************************************


# ***********************************************************************************************
# FUTURE
def get_location_info():
    location_info_flag = False
    cmd_status = True
    
    try:
        # -----------------------------------------------------------------------------------------------
        if cmd_status:
            pass
        # -----------------------------------------------------------------------------------------------
        
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('Exception: send_sms():', e)
    # -----------------------------------------------------------------------------------------------
    return sms_sent_flag
# ***********************************************************************************************
