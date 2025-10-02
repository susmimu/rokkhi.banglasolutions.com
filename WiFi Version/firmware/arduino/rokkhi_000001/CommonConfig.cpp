// ----------------------------------------------------------------------------------------------------
#include "CommonConfig.h"
// ----------------------------------------------------------------------------------------------------
// char storedSSID[32];                        // Define the variables (initialize here)
// char storedPassword[32];                    // Define the variables (initialize here)
// String SSID = "ZerOneLab";                  // Define the variables (initialize here)
// String PASSWORD = "zerone333";              // Define the variables (initialize here)
// ----------------------------------------------------------------------------------------------------
String device_sl = "000000";                   // This will be sent to Cloud for Login
String mac_original = "24:DC:C3:A1:42:70";
String mac_read = "";                          // This will be sent to Cloud for Login
// ----------------------------------------------------------------------------------------------------
// const char* serverIP = "192.168.1.101";                    // i-NUC
// const char* serverIP = "192.168.43.181";                // Nova2i
const char* serverIP = "rokkhi.banglasolutions.com";    // Initialization is here
const int serverPort = 6237;                               // Initialization is here
// ----------------------------------------------------------------------------------------------------
byte motion_capture_active = 0;
byte motion_capture_flash = 0;

int no_of_frame_capture_limit = 0;

int hb_delay_cnt = 0;
// ----------------------------------------------------------------------------------------------------
bool motionDetected = false;
camera_fb_t *fb = NULL;                     // This buffer has global use
// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
void configure_wdt(int time_out_in_sec)
{
  esp_task_wdt_config_t config_wdt = {.timeout_ms = time_out_in_sec * 1000, .trigger_panic = true,};

  // Initialize the Task Watchdog Timer
  esp_task_wdt_deinit();
  esp_task_wdt_init(&config_wdt);   // Enable panic so ESP32 resets
  esp_task_wdt_add(NULL);   // Add the current task (loop task) to WDT
  esp_task_wdt_reconfigure(&config_wdt);
  esp_task_wdt_add(NULL);   // Add the current task (loop task) to WDT

  if (DEBUG)
  {
    Serial.printf("WDT Init with a delay of %d Seconds\n", time_out_in_sec);
  }
}
// ***********************************************************************************************


// ***********************************************************************************************
void check_mac_validity(void)
{
  // Read the ESP32 MAC address
  mac_read = WiFi.macAddress();
  // Print the MAC address to the Serial Monitor
  if (DEBUG)
    Serial.println("\nmac_read: " + mac_read);

  // Check is this ESP is ORIGINAL
  if (mac_read == mac_original) 
  {
    if (DEBUG)
      Serial.println("Original ESP found :)");
  }
  else
  {
    while(1)
    {
      // esp_task_wdt_reset();
      // WDT Should Reboot the System, Incase of reading problem it may be fixed after reboot

      if (DEBUG)
        Serial.println("Duplicate ESP Detected :(");

      delay(10000);
    }
  }
}
// ***********************************************************************************************


// ***********************************************************************************************
void flashLightSignal(int count)
{
  if (DEBUG)
    Serial.printf("Flashing for %d Times\n", count);

  for (int i = 0; i < count; i++)
  {
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(500);
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(500);
  }
}
// ***********************************************************************************************


// ***********************************************************************************************
bool detectMotionByPIR(void)
{
  int motion_status = digitalRead(PIR_PIN);

  if (DEBUG)
  {
    Serial.print("motion_status: ");
    Serial.println(motion_status);
  }
  // ----------------------------------------------------------------------------------------------------
  if (motion_status == 0)
  {
    Serial.println("Motion Detected");
    return true;
  }
  else
  {
    Serial.println("No Motion");
    return false;
  }
  // ----------------------------------------------------------------------------------------------------
}
// ***********************************************************************************************
