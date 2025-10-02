import camera
import time
import machine
import os
import gc
from machine import Pin, WDT, RTC
import camera
import time
import esp32


init_status = camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
print('init_status:', init_status)
# Flip up side down
camera.flip(1)
# Left / Right
camera.mirror(1)
# -----------------------------------------------------------------------------------------------
# Framesize
camera.framesize(10)
# 1 = 160x120, 2 = 176x144, 3 = 240x176, 4 = 240x240, 5 = 320x240, 6 = 400x296, 7 = 480x320, 8 = 640x480, 9 = 800x600, 10 = 1024x768, 11 = 1280x720, 12 = 1280x1024, 13 = 1600x1200  (This is the Max Value)
# Check this link for more information: https://bit.ly/2YOzizz
# -----------------------------------------------------------------------------------------------
# Special effects
camera.speffect(camera.EFFECT_NONE)
# The options are the following:
# EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO
# -----------------------------------------------------------------------------------------------
# White balance
camera.whitebalance(camera.WB_NONE)
# The options are the following:
# WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME
# -----------------------------------------------------------------------------------------------
# Saturation
camera.saturation(0)
# -2,2 (default 0). -2 grayscale 
# -----------------------------------------------------------------------------------------------
# Brightness
camera.brightness(0)
# -2,2 (default 0). 2 brightness
# -----------------------------------------------------------------------------------------------
# Contrast
camera.contrast(0)
# -2,2 (default 0). 2 highcontrast
# -----------------------------------------------------------------------------------------------
# quality
camera.quality(10)
# 4~63, Lower the value higher the quality
# -----------------------------------------------------------------------------------------------
print('Camera init success! :)')

print("gc.mem_free():", gc.mem_free(), "Bytes")
print("gc.mem_free():", (gc.mem_free() / 1048576), "MB")
# Without PSRAM → around 100 KB free.
# With PSRAM → a few MB free (e.g., 4 MB).
# -----------------------------------------------------------------------------------------------
print("esp32.idf_heap_info(esp32.HEAP_DATA):", esp32.idf_heap_info(esp32.HEAP_DATA))
# -----------------------------------------------------------------------------------------------



flash_light = Pin(4, Pin.OUT)
flash_light.value(False)


flash_light.value(True)
#time.sleep(1)
pic = camera.capture()
pic = camera.capture()
pic = camera.capture()
pic = camera.capture()
pic = camera.capture()
pic = camera.capture()

# print('Pic:', pic)
f = open('/photo.jpeg', 'wb')
f.write(pic)
f.close()
flash_light.value(False)

camera.deinit()




