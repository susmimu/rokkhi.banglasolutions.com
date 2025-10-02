# -----------------------------------------------------------------------------------------------
from time import sleep
from machine import Pin
from machine import UART
# -----------------------------------------------------------------------------------------------
uart1 = ''


# -----------------------------------------------------------------------------------------------
modem_rst_pin = Pin(15, Pin.OUT)
modem_rst_pin.off()
sleep(1)
modem_rst_pin.on()
# sleep(1)
print('Modem restart success :)')
# -----------------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------------

sleep(30)

try:
    uart1 = UART(1, baudrate=115200, parity=None, timeout=10000, stop=1, tx=12, rx=13)
    print('UART init success!')
except Exception as e:
    print('UART init failed!')
    print('e:', e)


while True:
    print('CMD>', 'AT+CUSD=1\r\n')
    
    uart1.write('AT+CUSD=1\r\n')
    
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)
    
    
    uart1.write('AT+CUSD=1,"*551#"\r\n')
    
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)
    reply_byte = uart1.readline()
    print('reply_byte:', reply_byte)   
    print('---------------------------------------------')
    sleep(10)
# -----------------------------------------------------------------------------------------------

