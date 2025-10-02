// ----------------------------------------------------------------------------------------------------
#ifndef EEPROMMANAGER_H
#define EEPROMMANAGER_H
// ----------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------
#include <EEPROM.h>
// #include <Arduino.h>
#include "CommonConfig.h"
#include "WiFiManager.h"
// ----------------------------------------------------------------------------------------------------
#define EEPROM_SIZE   100           // Reserve 100 bytes for SSID & Password

#define SSID_ADDR       0           // Start address for SSID
#define PASS_ADDR      25           // Start address for Password

#define MOT_ALRT_STATUS_ADDR 51     // Start address for Password
#define MOT_ALRT_FLASH_ADDR  56     // Start address for Password

#define NO_OF_FRAME_ADDR 61

#define HB_DELAY_ADDR 66
// ----------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------
// Function prototypes
void read_config_from_eeprom_to_variables(void);
void writeByteToEEPROM(int address, byte value);
void writeStringToEEPROM(int addr, const String &data);
void writeIntToEEPROM(int address, int value);

// ----------------------------------------------------------------------------------------------------
#endif
// ----------------------------------------------------------------------------------------------------
