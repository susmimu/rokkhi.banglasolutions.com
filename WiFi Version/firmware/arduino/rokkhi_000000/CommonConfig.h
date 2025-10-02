// ----------------------------------------------------------------------------------------------------
#ifndef COMMONCONFIG_H
#define COMMONCONFIG_H
// ----------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------
#include <Arduino.h>
#include "esp_camera.h"
#include <esp_task_wdt.h>
#include <WiFi.h>
// ----------------------------------------------------------------------------------------------------
#define DEBUG 1
// #define DEBUG 0

#if DEBUG
  #define DEBUG_PRINT(x)    Serial.print(x)
  #define DEBUG_PRINTLN(x)  Serial.println(x)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
#endif
// ----------------------------------------------------------------------------------------------------
#define STATUS_LED_PIN  15 
#define PIR_PIN         14  // IT MUST NOT Change
#define AC_STATUS_PIN   13 
#define RELAY_PIN        2 
#define FLASH_LGT_PIN    4  // Built in Flash Also in this PIN
// ----------------------------------------------------------------------------------------------------
extern String mac_read;         // Declare the variable (no initialization)
extern String device_sl;        // Declare the variable (no initialization)
// ----------------------------------------------------------------------------------------------------
extern byte motion_capture_active;
extern byte motion_capture_flash;

extern int no_of_frame_capture_limit;

extern int hb_delay_cnt;

extern String full_hb_reply_from_server;
// ----------------------------------------------------------------------------------------------------
extern camera_fb_t *fb;         // This buffer has global use
extern bool motionDetected;
// ----------------------------------------------------------------------------------------------------
extern const char* serverIP ;   // My Local Development PC
extern const int serverPort;    // Initialization is here
// ----------------------------------------------------------------------------------------------------

// Function prototypes
void configure_wdt(int time_out_in_sec);
void check_mac_validity(void);
void flashLightSignal(int count);
bool detectMotionByPIR(void);




// ----------------------------------------------------------------------------------------------------
#endif
// ----------------------------------------------------------------------------------------------------
