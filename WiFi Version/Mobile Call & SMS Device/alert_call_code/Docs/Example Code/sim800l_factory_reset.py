# -----------------------------------------------------------------------------------------------
from time import sleep
from machine import Pin
from machine import UART
# -----------------------------------------------------------------------------------------------
modem_rst_pin = Pin(15, Pin.OUT)   # create output pin on GPIO15
modem_rst_pin.on()                 # set pin to "on" (high) level
# modem_rst_pin.off()              # set pin to "off" (low) level
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
uart1 = ''

try:
    uart1 = UART(1, baudrate=115200, parity=None, timeout=15000, stop=1, tx=12, rx=13)
    print('UART init success!')
except Exception as e:
    print('UART init failed!')
    print('e:', e)
# -----------------------------------------------------------------------------------------------
print('Modem restarting...')
modem_rst_pin.off()
sleep(1)
modem_rst_pin.on()
sleep(15)
# -----------------------------------------------------------------------------------------------
reply_byte = uart1.read(500)
print('Initial data:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', 'AT\r\n')
uart1.write('AT\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', 'AT&F0\r\n')
uart1.write('AT&F0\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
'''
print('CMD>', 'ATE0&W\r\n')
uart1.write('ATE0&W\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', '+CLTS=1\r\n')
uart1.write('+CLTS=1\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', '&W=1\r\n')
uart1.write('&W=1\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', '&W\r\n')
uart1.write('&W\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
print('CMD>', '+CFUN=0\r\n')
uart1.write('+CFUN=0\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
'''

print('CMD>', '+CFUN=1,1\r\n')
uart1.write('+CFUN=1,1\r\n')
reply_byte = uart1.read(500)
print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------

while True:
    print('CMD>', 'AT\r\n')
    uart1.write('AT\r\n')
    reply_byte = uart1.read(500)
    print('reply_byte:', reply_byte)
# -----------------------------------------------------------------------------------------------
