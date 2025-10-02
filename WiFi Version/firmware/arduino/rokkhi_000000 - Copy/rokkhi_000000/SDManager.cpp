// ----------------------------------------------------------------------------------------------------
#include "SDManager.h"
// ----------------------------------------------------------------------------------------------------
// // const char* serverIP = "192.168.1.106";                 // My Local Development PC
// const char* serverIP = "rokkhi.banglasolutions.com";    // Initialization is here
// const int serverPort = 4231;                            // Initialization is here
// ----------------------------------------------------------------------------------------------------



// ***********************************************************************************************
void initializedSD_MMC(void)
{
  // ----------------------------------------------------------------------------------------------------
  if (DEBUG)
    Serial.println("Starting SD Card");
  
  if (!SD_MMC.begin()) 
  {
    if (DEBUG)
      Serial.println("Card Mount Failed");

    return;
  }
  // ----------------------------------------------------------------------------------------------------
  uint8_t cardType = SD_MMC.cardType();

  if (cardType == CARD_NONE) 
  {
    if (DEBUG)
      Serial.println("No SD_MMC card attached");
    
    return;
  }
  // ----------------------------------------------------------------------------------------------------
  if (DEBUG)
    Serial.print("SD_MMC Card Type: ");
  
  if (cardType == CARD_MMC) 
  {
    if (DEBUG)
      Serial.println("MMC");
  } 
  else if (cardType == CARD_SD) 
  {
    if (DEBUG)
      Serial.println("SDSC");
  } 
  else if (cardType == CARD_SDHC) 
  {
    if (DEBUG)
      Serial.println("SDHC");
  } 
  else 
  {
    if (DEBUG)
      Serial.println("UNKNOWN");
  }
}
// ***********************************************************************************************


// ***********************************************************************************************
void unmountSD_MMC(void)
{
  SD_MMC.end();

  if (DEBUG)
    Serial.println("SD Card Unmounted OK");
}
// ***********************************************************************************************


// ***********************************************************************************************
void delete_all_files_in_root_dir()
{
  // ----------------------------------------------------------------------------------------------------
  File root = SD_MMC.open("/");

  if (!root)
  {
    if (DEBUG)
      Serial.println("Failed to open root directory");

    return;
  }
  // ----------------------------------------------------------------------------------------------------
  while (true) 
  {
    File entry = root.openNextFile();

    if (!entry)
    {
      break;  // No more files
    }
    // ----------------------------------------------------------------------------------------------------
    if (!entry.isDirectory()) 
    {
      // Construct the full file path
      String filePath = "/" + String(entry.name()); // Ensure leading "/"

      if (DEBUG)
      {
        Serial.print("Deleting file: ");
        Serial.println(filePath);
      }
      
      // Convert String to const char* and delete the file
      if (SD_MMC.remove(filePath.c_str())) 
      {
        if (DEBUG)
          Serial.println("File deleted successfully.");
      } 
      else 
      {
        if (DEBUG)
          Serial.println("Failed to delete file.");
      }
    } 
    // ----------------------------------------------------------------------------------------------------
    else 
    {
      if (DEBUG)
      {
        Serial.print("Skipping directory: ");
        Serial.println(entry.name());
      }        
    }
    // ----------------------------------------------------------------------------------------------------
    entry.close();
    delay(10);
  }
  // ----------------------------------------------------------------------------------------------------
  root.close();
}
// ***********************************************************************************************
