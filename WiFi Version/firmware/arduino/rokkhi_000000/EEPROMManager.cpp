// ----------------------------------------------------------------------------------------------------
#include "EEPROMManager.h"
// ----------------------------------------------------------------------------------------------------
// // const char* serverIP = "192.168.1.106";                 // My Local Development PC
// const char* serverIP = "rokkhi.banglasolutions.com";    // Initialization is here
// const int serverPort = 4231;                            // Initialization is here
// ----------------------------------------------------------------------------------------------------


/* 
Function	                      Description
---------------------------     ------------------------------------------
EEPROM.begin(size)	            Initializes EEPROM with the specified size
EEPROM.write(address, value)	  Writes a single byte
EEPROM.put(address, value)	    Writes any data type
EEPROM.read(address)	          Reads a single byte
EEPROM.get(address, variable)	  Reads any data type
EEPROM.commit()	                Saves changes (required on ESP32)
EEPROM.end()	                  Releases EEPROM memory
EEPROM.clear()	                (Manually loop through and reset memory)
*/


// ***********************************************************************************************
void initEEPROM(void)
{
  // Initialize EEPROM with the specified size
  EEPROM.begin(EEPROM_SIZE); 

  DEBUG_PRINT("EEPROM Initialized with Byte: ");
  DEBUG_PRINTLN(EEPROM_SIZE);
}
// ***********************************************************************************************


// ***********************************************************************************************
void deinitEEPROM(void)
{
  EEPROM.end();  // Releases EEPROM memory

  DEBUG_PRINTLN("EEPROM Releasesed");
}
// ***********************************************************************************************


// ***********************************************************************************************
void eraseAllEEPROMData(void)
{
  for (int i = 0; i < EEPROM_SIZE; i++)
  {
    EEPROM.write(i, 0xFF);  // Set all bytes to 0xFF
  }
  
  EEPROM.commit();          // Required on ESP32 to save changes

  DEBUG_PRINTLN("EEPROM Ereased");
}
// ***********************************************************************************************


// ***********************************************************************************************
void writeByteToEEPROM(int address, byte value)
{
  initEEPROM();
  
  EEPROM.write(address, value);
  EEPROM.commit();

  if (DEBUG)
  {
    DEBUG_PRINT("Written byte: ");
    DEBUG_PRINTLN(value);
  }

  deinitEEPROM();
}
// ***********************************************************************************************


// ***********************************************************************************************
byte readByteFromEEPROM(int address)
{
  initEEPROM();
  
  byte value = EEPROM.read(address);

  DEBUG_PRINT("Read byte: ");
  DEBUG_PRINTLN(value);

  deinitEEPROM();

  return value;
}
// ***********************************************************************************************


// ***********************************************************************************************
void writeStringToEEPROM(int addr, const String &data) 
{
  initEEPROM();

  for (int i = 0; i < data.length(); ++i) 
  {
    EEPROM.write(addr + i, data[i]);
  }

  EEPROM.write(addr + data.length(), '\0');  // Null-terminate
  
  EEPROM.commit();
  deinitEEPROM();
}
// ***********************************************************************************************


// ***********************************************************************************************
String readStringFromEEPROM(int addr) 
{
  initEEPROM();

  String data = "";
  char ch;

  while ((ch = EEPROM.read(addr++)) != '\0') 
  {
    data += ch;
  }

  deinitEEPROM();

  return data;
}
// ***********************************************************************************************


// ***********************************************************************************************
void writeIntToEEPROM(int address, int value)
{
  initEEPROM();

  EEPROM.write(address, (value >> 0) & 0xFF);
  EEPROM.write(address + 1, (value >> 8) & 0xFF);

  EEPROM.commit();  // Important!
  deinitEEPROM();
}
// ***********************************************************************************************


// ***********************************************************************************************
int readIntFromEEPROM(int address) 
{
  initEEPROM();

  int value = EEPROM.read(address);
  value |= (EEPROM.read(address + 1) << 8);

  deinitEEPROM();

  return value;
}
// ***********************************************************************************************


// ***********************************************************************************************
void read_config_from_eeprom_to_variables(void)
{
  SSID = readStringFromEEPROM(SSID_ADDR);
  PASSWORD = readStringFromEEPROM(PASS_ADDR);
  // ----------------------------------------------------------------------------------------------------
  motion_capture_active = readByteFromEEPROM(MOT_ALRT_STATUS_ADDR);
  // // Fresh EEPROM Value Overwrite
  // if (motion_capture_active == 255)
  // {
  //   motion_capture_active = 1;
  // }
  // ----------------------------------------------------------------------------------------------------
  motion_capture_flash  = readByteFromEEPROM(MOT_ALRT_FLASH_ADDR);
  // // Fresh EEPROM Value Overwrite
  // if (motion_capture_flash == 255)
  // {
  //   motion_capture_flash = 1;
  // }
  // ----------------------------------------------------------------------------------------------------
  no_of_frame_capture_limit = readIntFromEEPROM(NO_OF_FRAME_ADDR);
  // // Fresh EEPROM Value Overwrite
  // if (no_of_frame_capture_limit == 65535)
  // {
  //   no_of_frame_capture_limit = 30;
  // }
  // ----------------------------------------------------------------------------------------------------
  hb_delay_cnt = readIntFromEEPROM(HB_DELAY_ADDR);
  // Fresh EEPROM Value Overwrite
  if (hb_delay_cnt == 65535)
  {
    hb_delay_cnt = 10;
  }
  // ----------------------------------------------------------------------------------------------------  
}
// ***********************************************************************************************
