// ----------------------------------------------------------------------------------------------------
#include <Arduino.h>
#include "CommonConfig.h"
#include "WiFiManager.h"
#include "CameraManager.h"
#include "soc/rtc_cntl_reg.h"
#include "CloudManager.h"
#include "esp_system.h"
#include "EEPROMManager.h"
// ----------------------------------------------------------------------------------------------------
pixformat_t pixel_format;
framesize_t frame_size;
int hmirror;
int vflip;
// ----------------------------------------------------------------------------------------------------
bool motion_info_sent_to_server_f = false;
int hb_counter = 0;
int cloud_connection_lost_cnt = 0;
// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
/* Function Prototypes
✅ Place function prototypes at the top, before setup() and loop()
❌ Never put them inside setup() or loop()
*/
void execute_command_based_on_hb_reply(void);
// ***********************************************************************************************


// ***********************************************************************************************
void setup() 
{
  // ----------------------------------------------------------------------------------------------------
  Serial.begin(115200);
  // ----------------------------------------------------------------------------------------------------
  read_config_from_eeprom_to_variables();
  // ----------------------------------------------------------------------------------------------------
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, HIGH);

  pinMode(PIR_PIN, INPUT);
  // pinMode(PIR_PIN, INPUT_PULLDOWN);

  pinMode(AC_STATUS_PIN, INPUT);
  // pinMode(AC_STATUS_PIN, INPUT_PULLUP);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  pinMode(FLASH_LGT_PIN, OUTPUT);
  digitalWrite(FLASH_LGT_PIN, LOW);
  // ----------------------------------------------------------------------------------------------------
  DEBUG_PRINTLN("Single Flash to Check Power!");

  flashLightSignal(1);
  // ----------------------------------------------------------------------------------------------------
  if (psramFound())
  {
    DEBUG_PRINTLN("✅ PSRAM is ENABLED and detected!");
  } 
  else 
  {
    DEBUG_PRINTLN("❌ PSRAM is NOT available!");
  }
  // ----------------------------------------------------------------------------------------------------
  // Disable brownout detector
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  DEBUG_PRINTLN("Brownout detector disabled.");
  // ----------------------------------------------------------------------------------------------------
  configure_wdt(180);  // 1 = 1 Second; 3 Minutes Here
  // ----------------------------------------------------------------------------------------------------
  if (!connectToWiFi())
  {
    check_mac_validity();
    startAPMode();

    while (true)
    {
      // Do not Reset WDT here (esp_task_wdt_reset();). 
      // So, System will Reboot if temporarily failed to connect with Router.
      server.handleClient();
    }
  }
  // ----------------------------------------------------------------------------------------------------
  // If Successfully connect to WiFi
  check_mac_validity();
  connect_to_cloud();
  // ----------------------------------------------------------------------------------------------------
  if (login_to_cloud())
  {
    // Init camera. It should be called single time
    pixel_format = PIXFORMAT_JPEG;  // JPEG
    // Note: If Camera Memory Overflow use FRAMESIZE_VGA else can use FRAMESIZE_SVGA
    // frame_size = FRAMESIZE_CIF;   // 400x296
    // frame_size = FRAMESIZE_HVGA;  // 480x320
    frame_size = FRAMESIZE_VGA;   // 640x480;
    // frame_size = FRAMESIZE_SVGA;  // 800x600; 
    hmirror = 1;
    vflip = 1;

    initializeCameraWithParams(pixel_format, frame_size, hmirror, vflip);
  }
  // If Login FAILED Device will Restart. So, next codes will not execute.
  // ----------------------------------------------------------------------------------------------------
  // configure_wdt(60);  // 1 = 1 Second; 1 Minute Here
  // ----------------------------------------------------------------------------------------------------
  // This delay Should be for WiFi Stabilization for Cloud Connection
  delay(1000);
}
// ***********************************************************************************************


// ***********************************************************************************************
void loop()
{
  // ====================================================================================================
  // Reset the watchdog timer periodically to avoid restart
  delay(1000);
  esp_task_wdt_reset();
  hb_counter++;
  // ====================================================================================================


  // ====================================================================================================
  if (!client.connected())
  {
    cloud_connection_lost_cnt++;
    digitalWrite(FLASH_LGT_PIN, LOW);   // OFF Flash Light if somehow ON before
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINT("Cloud connection LOST Counter: ");
    DEBUG_PRINTLN(cloud_connection_lost_cnt);
    // ----------------------------------------------------------------------------------------------------
    if (cloud_connection_lost_cnt > 10)
    {
      DEBUG_PRINTLN("Opps! Device NOT Connected to the Cloud!\nRebooting...");      
      ESP.restart();
    }
  }
  else
  {
    cloud_connection_lost_cnt = 0;
  }
  // ====================================================================================================


  // ====================================================================================================
  // Send HB to Server
  DEBUG_PRINT("hb_counter >>>: ");
  DEBUG_PRINTLN(hb_counter);
  // ----------------------------------------------------------------------------------------------------
  if (hb_counter >= hb_delay_cnt)
  {
    hb_counter = 0;
    String hb_text = "hB";
    // ----------------------------------------------------------------------------------------------------
    digitalWrite(FLASH_LGT_PIN, LOW);   // OFF Flash Light if somehow ON before
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINTLN("Sending HB to Server and Waiting for Reply...");

    if (sendFlagToServerAndWaitForReply(hb_text))
    {
      DEBUG_PRINTLN("Server successfully received HB :)");
      // ----------------------------------------------------------------------------------------------------
      execute_command_based_on_hb_reply();
    }
  }
  // ====================================================================================================


  // ====================================================================================================
  // This part will work on Motion Detection by PIR
  DEBUG_PRINTLN("-----------------------------------------");
  DEBUG_PRINT("hb_delay_cnt: ");
  DEBUG_PRINTLN(hb_delay_cnt);

  DEBUG_PRINT("motion_capture_active: ");
  DEBUG_PRINTLN(motion_capture_active);

  DEBUG_PRINT("motion_capture_flash: ");
  DEBUG_PRINTLN(motion_capture_flash);

  DEBUG_PRINT("no_of_frame_capture_limit: ");
  DEBUG_PRINTLN(no_of_frame_capture_limit);
  DEBUG_PRINTLN("-----------------------------------------");
  // ----------------------------------------------------------------------------------------------------
  // If Motion Alert is Active (Read from EEPROM)
  if (motion_capture_active == 1)
  {
    while (detectMotionByPIR())
    {
      motion_info_sent_to_server_f = false;
      bool server_confirmed_start_img_flag = false;
      int total_no_of_frames = 0;
      // ----------------------------------------------------------------------------------------------------
      DEBUG_PRINTLN("Motion Detected! Informing the Server and Waiting for response...");
      // ----------------------------------------------------------------------------------------------------
      // Only execute if "motion_info_sent_to_server_f" is False
      if (!motion_info_sent_to_server_f)  
      {
        if (sendFlagToServerAndWaitForReply("MoTionYeS"))
        {
          DEBUG_PRINTLN("Server successfully informed about Motion :)");

          // Set the Flag. So prevent multiple execution
          motion_info_sent_to_server_f = true;
          hb_counter = 0;
        }
      }
      // ----------------------------------------------------------------------------------------------------


      // ----------------------------------------------------------------------------------------------------
      // Server Already informed about Motion
      if (motion_info_sent_to_server_f)
      {
        DEBUG_PRINTLN("Tell Server to Save Images and Waiting for response...");

        if (sendFlagToServerAndWaitForReply("mOtImGsTaRt"))
        {
          DEBUG_PRINTLN("Server successfully informed to Save Images :)");

          server_confirmed_start_img_flag = true;
          hb_counter = 0;
        }
      }
      // ----------------------------------------------------------------------------------------------------


      // ----------------------------------------------------------------------------------------------------
      // Server is Ready to Receive and Save ImageFrames
      if (server_confirmed_start_img_flag)
      {
        // ----------------------------------------------------------------------------------------------------
        // Control FLASH Light
        if (motion_capture_flash == 1)
        {
          digitalWrite(FLASH_LGT_PIN, HIGH);
          DEBUG_PRINTLN("Flash Light ON");
        }
        else
        {
          digitalWrite(FLASH_LGT_PIN, LOW);
          DEBUG_PRINTLN("Flash Light OFF");
        }
        // ----------------------------------------------------------------------------------------------------
        camera_fb_t *fb;

        while (detectMotionByPIR() && (total_no_of_frames < no_of_frame_capture_limit))
        {
          fb = esp_camera_fb_get();
          // ----------------------------------------------------------------------------------------------------
          if (!fb)
          {
            break;
          }
          else
          {
            // ----------------------------------------------------------------------------------------------------
            DEBUG_PRINT("Image size: ");
            DEBUG_PRINT(fb->len);
            DEBUG_PRINTLN(" bytes");
            DEBUG_PRINT((fb->len / 1024.0, 2)); // 2 decimal places
            DEBUG_PRINTLN(" KB");
            // ----------------------------------------------------------------------------------------------------
            // client.write("IMG", 3);            // Send marker before sending size
            client.write((uint8_t*)&fb->len, 4);  // Send Size
            client.write(fb->buf, fb->len);       // Send Data
            esp_camera_fb_return(fb);
          }
          // ----------------------------------------------------------------------------------------------------
          delay(3);  // ADJUST AS REQUIRED
          /* Restrict to number of Frames to be sent as MJPEG, Although continuous motion. 
          So file size will be fixed and No risk of WDT reset and file corruption
          */
          total_no_of_frames++;

          DEBUG_PRINT("total_no_of_frames: ");
          DEBUG_PRINTLN(total_no_of_frames);
        }
        // ----------------------------------------------------------------------------------------------------
        // Motion END, or Frame Limit Reached. Upper Loop Broken. Inform Server that no more Motion Image Left
        digitalWrite(FLASH_LGT_PIN, LOW);

        DEBUG_PRINTLN("Flash Light OFF");
        // ----------------------------------------------------------------------------------------------------
        DEBUG_PRINTLN("All Frames Sent! Telling Server to STOP Saving and Waiting for response...");
        // ----------------------------------------------------------------------------------------------------
        if (sendFlagToServerAndWaitForReply("eNdM"))
        {
          DEBUG_PRINTLN("Server successfully informed to Stop Saving :)");

          // A small delay for next motion frames
          delay(1000);
        }
        // ----------------------------------------------------------------------------------------------------
        hb_counter = 0;
      }
    }
  }
  else
  {
    DEBUG_PRINTLN("Motion Alert NOT Actived");
    digitalWrite(FLASH_LGT_PIN, LOW);   // OFF Flash Light if somehow ON before
  }
  // ====================================================================================================
}
// ***********************************************************************************************


// ***********************************************************************************************
void execute_command_based_on_hb_reply(void)
{
  // ----------------------------------------------------------------------------------------------------
  String dElaYhB = "dElaYhB";
  String mOtioNcONf = "mOtioNcONf";
  String fRameCApLiM = "fRameCApLiM";
  String lgtAlrmChaLu = "lgtAlrmChaLu";
  String lgtAlrmBOnDhO = "lgtAlrmBOnDhO";
  String cApPiC = "cApPiC";
  // ----------------------------------------------------------------------------------------------------
  if(full_hb_reply_from_server.indexOf(mOtioNcONf) >= 0)
  {
    DEBUG_PRINTLN("Server asked for Motion Config");
    // ----------------------------------------------------------------------------------------------------
    // Motion Capture Active Status Change
    if(full_hb_reply_from_server.indexOf("MaS_On") >= 0)
    {
      motion_capture_active = 1;
      DEBUG_PRINTLN("Motion Capture ENABLED");
    }
    else if(full_hb_reply_from_server.indexOf("MaS_oFF") >= 0)
    {
      motion_capture_active = 0;
      DEBUG_PRINTLN("Motion Capture DISABLED");
    }
    // ----------------------------------------------------------------------------------------------------
    // Motion Capture Flash Status Change
    if(full_hb_reply_from_server.indexOf("mcf_oN") >= 0)
    {
      motion_capture_flash = 1;
      DEBUG_PRINTLN("Motion Capture Flash ON");
    }
    else if(full_hb_reply_from_server.indexOf("mcf_OfF") >= 0)
    {
      motion_capture_flash = 0;
      DEBUG_PRINTLN("Motion Capture Flash OFF");
    }
    // ----------------------------------------------------------------------------------------------------
    // Write and Read in EEPROM
    writeByteToEEPROM(MOT_ALRT_STATUS_ADDR, motion_capture_active);
    writeByteToEEPROM(MOT_ALRT_FLASH_ADDR, motion_capture_flash);
    read_config_from_eeprom_to_variables();
    // ----------------------------------------------------------------------------------------------------
    size_t bytesSent = client.write(mOtioNcONf.c_str(), mOtioNcONf.length());

    DEBUG_PRINT("bytesSent: ");
    DEBUG_PRINTLN(bytesSent);

    if (bytesSent == mOtioNcONf.length())
    {
      DEBUG_PRINTLN("Motion Config reply sent OK");
    }
    // ----------------------------------------------------------------------------------------------------
  }
  // ----------------------------------------------------------------------------------------------------
  else if(full_hb_reply_from_server.indexOf(fRameCApLiM) >= 0)
  {
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINTLN("Server asked to Update No of Frame to be Captured");
    // ----------------------------------------------------------------------------------------------------
    int startIndex = 0;
    int commaIndex = 0;
    int part_cnt = 0;
    // ----------------------------------------------------------------------------------------------------
    while ((commaIndex = full_hb_reply_from_server.indexOf(',', startIndex)) != -1)
    {
      String part = full_hb_reply_from_server.substring(startIndex, commaIndex);
      DEBUG_PRINTLN(part);
      startIndex = commaIndex + 1;
      DEBUG_PRINTLN(startIndex);
      DEBUG_PRINTLN(commaIndex);

      if (part_cnt == 2)
      {
        no_of_frame_capture_limit = part.toInt();  // Convert to integer
      }

      part_cnt++;
      DEBUG_PRINTLN(part_cnt);
    }
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINT("no_of_frame_capture_limit: ");
    DEBUG_PRINTLN(no_of_frame_capture_limit);
    // ----------------------------------------------------------------------------------------------------
    writeIntToEEPROM(NO_OF_FRAME_ADDR, no_of_frame_capture_limit);
    read_config_from_eeprom_to_variables();
    // ----------------------------------------------------------------------------------------------------
    size_t bytesSent = client.write(fRameCApLiM.c_str(), fRameCApLiM.length());

    DEBUG_PRINT("bytesSent: ");
    DEBUG_PRINTLN(bytesSent);

    if (bytesSent == fRameCApLiM.length())
    {
      DEBUG_PRINTLN("No of Frame reply sent OK");
    }
  }
  // ----------------------------------------------------------------------------------------------------
  else if(full_hb_reply_from_server.indexOf(dElaYhB) >= 0)
  {
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINTLN("Server asked to Update HB Delay");
    // ----------------------------------------------------------------------------------------------------
    int startIndex = 0;
    int commaIndex = 0;
    int part_cnt = 0;
    // ----------------------------------------------------------------------------------------------------
    while ((commaIndex = full_hb_reply_from_server.indexOf(',', startIndex)) != -1)
    {
      String part = full_hb_reply_from_server.substring(startIndex, commaIndex);
      DEBUG_PRINTLN(part);
      startIndex = commaIndex + 1;
      DEBUG_PRINTLN(startIndex);
      DEBUG_PRINTLN(commaIndex);
      if (part_cnt == 2)
      {
        hb_delay_cnt = part.toInt();  // Convert to integer
      }

      part_cnt++;
      DEBUG_PRINTLN(part_cnt);
    }
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINT("hb_delay_cnt: ");
    DEBUG_PRINTLN(hb_delay_cnt);
    // ----------------------------------------------------------------------------------------------------
    writeIntToEEPROM(HB_DELAY_ADDR, hb_delay_cnt);
    read_config_from_eeprom_to_variables();
    // ----------------------------------------------------------------------------------------------------
    size_t bytesSent = client.write(dElaYhB.c_str(), dElaYhB.length());

    DEBUG_PRINT("bytesSent: ");
    DEBUG_PRINTLN(bytesSent);

    if (bytesSent == dElaYhB.length())
    {
      DEBUG_PRINTLN("HB Delay reply sent OK");
    }
  }
  // ----------------------------------------------------------------------------------------------------
  else if(full_hb_reply_from_server.indexOf(lgtAlrmChaLu) >= 0)
  {
    DEBUG_PRINTLN("Server asked for Light & Alarm ON");
    // ----------------------------------------------------------------------------------------------------
    digitalWrite(RELAY_PIN, HIGH);
    size_t bytesSent = client.write(lgtAlrmChaLu.c_str(), lgtAlrmChaLu.length());

    DEBUG_PRINT("bytesSent: ");
    DEBUG_PRINTLN(bytesSent);

    if (bytesSent == lgtAlrmChaLu.length())
    {
      DEBUG_PRINTLN("Light & Alarm ON and Reply sent OK");
    }        
  }
  // ----------------------------------------------------------------------------------------------------
  else if(full_hb_reply_from_server.indexOf(lgtAlrmBOnDhO) >= 0)
  {
    DEBUG_PRINTLN("Server asked for Light & Alarm OFF");
    // ----------------------------------------------------------------------------------------------------
    digitalWrite(RELAY_PIN, LOW);
    size_t bytesSent = client.write(lgtAlrmBOnDhO.c_str(), lgtAlrmBOnDhO.length());

    DEBUG_PRINT("bytesSent: ");
    DEBUG_PRINTLN(bytesSent);

    if (bytesSent == lgtAlrmBOnDhO.length())
    {
      DEBUG_PRINTLN("Light & Alarm OFF and Reply sent OK");
    }
  }
  // ----------------------------------------------------------------------------------------------------
  // If "cApPiC" Text is present in "server_cmd_buf"
  else if(full_hb_reply_from_server.indexOf(cApPiC) >= 0)
  {
    // ----------------------------------------------------------------------------------------------------
    DEBUG_PRINTLN("Server asked for Photo");
    // ----------------------------------------------------------------------------------------------------
    manually_capture_image_and_send_to_server(full_hb_reply_from_server);
  }
  // ----------------------------------------------------------------------------------------------------
  else if(full_hb_reply_from_server.indexOf("CLOSED") >= 0)
  {
    DEBUG_PRINTLN("Connection CLOSED!\nRebooting...");
    
    delay(500);
    ESP.restart();
  }
}
// ***********************************************************************************************
