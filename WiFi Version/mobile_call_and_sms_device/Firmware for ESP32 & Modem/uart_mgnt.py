'''
uart = UART(1, 9600)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
UART.deinit()                                # Turn off the UART bus.

uart.readchar()     # read 1 character and returns it as an integer
uart.read(10)       # read 10 characters, returns a bytes object
uart.read()         # read all available characters, wait untill timeout occur
uart.readline()     # read a line
uart.readinto(buf)  # read and store into the given buffer
uart.any()          # returns the number of characters waiting

uart.writechar(42)  # write 1 character
uart.write('abc')   # write the 3 characters

Additional keyword-only parameters that may be supported by a port are:
tx specifies the TX pin to use.
rx specifies the RX pin to use.
rts specifies the RTS (output) pin to use for hardware receive flow control.
cts specifies the CTS (input) pin to use for hardware transmit flow control.
txbuf specifies the length in characters of the TX buffer.
rxbuf specifies the length in characters of the RX buffer.
timeout specifies the time to wait for the first character (in ms).
timeout_char specifies the time to wait between characters (in ms).
invert specifies which lines to invert.
flow specifies which hardware flow control signals to use. The value is a bitmask.

UART.deinit()
Turn off the UART bus.
'''
# -----------------------------------------------------------------------------------------------
from machine import UART
import machine
from time import sleep
# -----------------------------------------------------------------------------------------------
UART_DEBUG = True
# -----------------------------------------------------------------------------------------------
uart2 = ''
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def uart2_init():
    global uart2
    
    try:
        uart2 = UART(2, baudrate=115200, parity=None, timeout=30000, stop=1, tx=17, rx=16)

        if UART_DEBUG:
            print('UART2 init success :)')

        sleep(1)
    except Exception as e:
        if UART_DEBUG:
            print('UART2 init failed :(\nRebooting...')
            print('e:uart2_init():', e)

        machine.reset()
# ***********************************************************************************************


# ***********************************************************************************************
def uart2_deinit():
    global uart2
    
    try:
        uart2.deinit()

        if UART_DEBUG:
            print('UART2 deinit success :)')
    except Exception as e:
        if UART_DEBUG:
            print('UART2 deinit failed :(')
            print('e:uart2_deinit():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def write_to_uart2(data):
    try:
        global uart2        

        uart2.write(data)
    except Exception as e:
        if UART_DEBUG:
            print('UART2 write failed :(')
            print('e:write_to_uart2():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def read_x_byte_from_uart2(len):
    try:
        global uart2

        reply_data = uart2.read(len)
        
        return reply_data.decode('utf-8').strip()
    except Exception as e:
        if UART_DEBUG:
            print('UART2 read failed :(\nMay be Timeout!')
            print('e:read_x_byte_from_uart2():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def read_from_uart2_until(hex_byte):
    try:
        global uart2
        reply_data = bytearray()

        while True:
            read_byte = uart2.read(1)
            reply_data += read_byte

            if read_byte == hex_byte:
                return reply_data.decode('utf-8').strip()
    except Exception as e:
        if UART_DEBUG:
            print('UART2 read failed :(\nMay be Timeout!')
            print('e:read_from_uart2_until():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def read_from_uart2_until_specific_text(expected_text):
    try:
        global uart2
        reply_data = bytearray()

        while True:
            read_byte = uart2.read(1)
            reply_data += read_byte

            if expected_text in reply_data:
                return reply_data.decode('utf-8').strip()
    except Exception as e:
        if UART_DEBUG:
            print('UART2 read failed :(\nMay be Timeout!')
            print('e:read_from_uart2_until_specific_text():', e)
# ***********************************************************************************************


# ***********************************************************************************************
def read_line_from_uart2():
    try:
        global uart2
        
        reply_data = uart2.readline()

        return reply_data.decode('utf-8').strip()
    except Exception as e:
        if UART_DEBUG:
            print('UART2 read failed :(\nMay be Timeout!')
            print('e:read_line_from_uart2():', e)
# ***********************************************************************************************


# # -----------------------------------------------------------------------------------------------
# uart2_init()
# sleep(0.25)
# # write_to_uart2('Hello Hasan\r\n')
# write_to_uart2('AT\r\n')
#
# print(read_from_uart2_until_specific_text('OK\r\n'))
# # -----------------------------------------------------------------------------------------------
