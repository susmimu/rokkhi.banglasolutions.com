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
  if (DEBUG)
    Serial.println("Single Flash to Check Power!");

  flashLightSignal(1);
  // ----------------------------------------------------------------------------------------------------
  if (psramFound())
  {
    if (DEBUG)
      Serial.println("✅ PSRAM is ENABLED and detected!");
  } 
  else 
  {
    if (DEBUG)
      Serial.println("❌ PSRAM is NOT available!");
  }
  // ----------------------------------------------------------------------------------------------------
  // Disable brownout detector
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  if (DEBUG)
    Serial.println("Brownout detector disabled.");
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
    frame_size = FRAMESIZE_VGA;     // 640x480;
    // frame_size = FRAMESIZE_SVGA; // 800x600;
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
  // ----------------------------------------------------------------------------------------------------
  if (!client.connected())
  {
    cloud_connection_lost_cnt++;
    // ----------------------------------------------------------------------------------------------------
    if (DEBUG)
    {
      Serial.print("Cloud connection LOST Counter: ");
      Serial.println(cloud_connection_lost_cnt);
    }
    // ----------------------------------------------------------------------------------------------------
    if (cloud_connection_lost_cnt > 70)
    {
      if (DEBUG)
      {
        Serial.println("Opps! Device NOT Connected to the Cloud!\nRebooting...");
      }

      ESP.restart();
    }
  }
  else
  {
    cloud_connection_lost_cnt = 0;
  }
  // ----------------------------------------------------------------------------------------------------
  // Flash Light OFF Frequently
  // digitalWrite(EXTRA_FLASH_PIN, LOW);

  // if (DEBUG)
  //   Serial.println("Extra Flash Light OFF");
  // ====================================================================================================


  // ====================================================================================================
  // Send HB to Server
  if (DEBUG)
  {
    Serial.print("hb_counter >>>: ");
    Serial.println(hb_counter);
  }
  // ----------------------------------------------------------------------------------------------------
  if (hb_counter >= hb_delay_cnt)
  {
    hb_counter = 0;
    String hb_text = "hB";
    // ----------------------------------------------------------------------------------------------------
    if (DEBUG)
      Serial.println("Sending HB to Server and Waiting for Reply...");

    if (sendFlagToServerAndWaitForReply(hb_text))
    {
      if (DEBUG)
        Serial.println("Server successfully received HB :)");
    }
  }
  // ====================================================================================================


  // ====================================================================================================
  // This part will work on Motion Detection by PIR
  if (DEBUG)
  {
    Serial.println("-----------------------------------------");
    Serial.print("hb_delay_cnt: ");
    Serial.println(hb_delay_cnt);

    Serial.print("motion_capture_active: ");
    Serial.println(motion_capture_active);

    Serial.print("motion_capture_flash: ");
    Serial.println(motion_capture_flash);

    Serial.print("no_of_frame_capture_limit: ");
    Serial.println(no_of_frame_capture_limit);
    Serial.println("-----------------------------------------");
  }
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
      if (DEBUG)
        Serial.println("Motion Detected! Informing the Server and Waiting for response...");
      // ----------------------------------------------------------------------------------------------------
      // Only execute if "motion_info_sent_to_server_f" is False
      if (!motion_info_sent_to_server_f)  
      {
        if (sendFlagToServerAndWaitForReply("MoTionYeS"))
        {
          if (DEBUG)
            Serial.println("Server successfully informed about Motion :)");

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
        if (DEBUG)
          Serial.println("Tell Server to Save Images and Waiting for response...");

        if (sendFlagToServerAndWaitForReply("mOtImGsTaRt"))
        {
          if (DEBUG)
            Serial.println("Server successfully informed to Save Images :)");

          server_confirmed_start_img_flag = true;
          hb_counter = 0;
          // ----------------------------------------------------------------------------------------------------
          // Control FLASH Light
          if (motion_capture_flash == 1)
          {
            digitalWrite(FLASH_LGT_PIN, HIGH);

            if (DEBUG)
              Serial.println("Flash Light ON");
          }
          else
          {
            digitalWrite(FLASH_LGT_PIN, LOW);

            if (DEBUG)
              Serial.println("Flash Light OFF");
          }
        }
      }
      // ----------------------------------------------------------------------------------------------------


      // ----------------------------------------------------------------------------------------------------
      // Server is Ready to Receive and Save ImageFrames
      if (server_confirmed_start_img_flag)
      {
        camera_fb_t *fb;

        while (detectMotionByPIR() && (total_no_of_frames < no_of_frame_capture_limit))
        {
          fb = esp_camera_fb_get();

          if (fb)
          {
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

          if (DEBUG)
          {
            Serial.print("total_no_of_frames: ");
            Serial.println(total_no_of_frames);
          }
        }
        // ----------------------------------------------------------------------------------------------------
        // Motion END, or Frame Limit Reached. Upper Loop Broken. Inform Server that no more Motion Image Left
        digitalWrite(FLASH_LGT_PIN, LOW);

        if (DEBUG)
          Serial.println("Flash Light OFF");
        // ----------------------------------------------------------------------------------------------------
        if (DEBUG)
          Serial.println("All Frames Sent! Telling Server to STOP Saving and Waiting for response...");
        // ----------------------------------------------------------------------------------------------------
        if (sendFlagToServerAndWaitForReply("eNdM"))
        {
          if (DEBUG)
            Serial.println("Server successfully informed to Stop Saving :)");

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
    Serial.println("Motion Alert NOT Actived");
  }
  // ====================================================================================================
  

  // ====================================================================================================
  // Device will receive CMD Here
  // If device is connected to the server
  if (client.connected())
  {
    // ----------------------------------------------------------------------------------------------------
    // Received CMD from the Server
    // ----------------------------------------------------------------------------------------------------
    String server_cmd_buf;
    server_cmd_buf.clear();
    // Check if there is data from the server
    while (client.available())
    {
      server_cmd_buf = client.readStringUntil('\n');
      hb_counter = 0;

      if (DEBUG)
        Serial.println("server_cmd_buf: " + server_cmd_buf);
    }
    // ----------------------------------------------------------------------------------------------------


    // ----------------------------------------------------------------------------------------------------
    String dElaYhB = "dElaYhB";
    String mOtioNcONf = "mOtioNcONf";
    String fRameCApLiM = "fRameCApLiM";
    String lgtAlrmChaLu = "lgtAlrmChaLu";
    String lgtAlrmBOnDhO = "lgtAlrmBOnDhO";
    String cApPiC = "cApPiC";
    // ----------------------------------------------------------------------------------------------------
    if(server_cmd_buf.indexOf(mOtioNcONf) >= 0)
    {
      if (DEBUG)
        Serial.println("Server asked for Motion Config");
      // ----------------------------------------------------------------------------------------------------
      // Motion Capture Active Status Change
      if(server_cmd_buf.indexOf("MaS_On") >= 0)
      {
        motion_capture_active = 1;

        if (DEBUG)
          Serial.println("Motion Capture ENABLED");
      }
      else if(server_cmd_buf.indexOf("MaS_oFF") >= 0)
      {
        motion_capture_active = 0;

        if (DEBUG)
          Serial.println("Motion Capture DISABLED");
      }
      // ----------------------------------------------------------------------------------------------------
      // Motion Capture Flash Status Change
      if(server_cmd_buf.indexOf("mcf_oN") >= 0)
      {
        motion_capture_flash = 1;

        if (DEBUG)
          Serial.println("Motion Capture Flash ON");
      }
      else if(server_cmd_buf.indexOf("mcf_OfF") >= 0)
      {
        motion_capture_flash = 0;

        if (DEBUG)
          Serial.println("Motion Capture Flash OFF");
      }
      // ----------------------------------------------------------------------------------------------------
      // Write and Read in EEPROM
      writeByteToEEPROM(MOT_ALRT_STATUS_ADDR, motion_capture_active);
      writeByteToEEPROM(MOT_ALRT_FLASH_ADDR, motion_capture_flash);
      read_config_from_eeprom_to_variables();
      // ----------------------------------------------------------------------------------------------------
      size_t bytesSent = client.write(mOtioNcONf.c_str(), mOtioNcONf.length());
  
      if (DEBUG)
        Serial.printf("bytesSent: %d\n", bytesSent);

      if (bytesSent == mOtioNcONf.length())
      {
        if (DEBUG)
          Serial.println("Motion Config reply sent OK");
      }
      // ----------------------------------------------------------------------------------------------------
    }
    // ----------------------------------------------------------------------------------------------------
    else if(server_cmd_buf.indexOf(fRameCApLiM) >= 0)
    {
      // ----------------------------------------------------------------------------------------------------
      if (DEBUG)
        Serial.println("Server asked to Update No of Frame to be Captured");
      // ----------------------------------------------------------------------------------------------------
      int startIndex = 0;
      int commaIndex = 0;
      int part_cnt = 0;
      // ----------------------------------------------------------------------------------------------------
      while ((commaIndex = server_cmd_buf.indexOf(',', startIndex)) != -1)
      {
        String part = server_cmd_buf.substring(startIndex, commaIndex);
        // Serial.println(part);
        startIndex = commaIndex + 1;
        // Serial.println(startIndex);
        // Serial.println(commaIndex);
        if (part_cnt == 1)
        {
          no_of_frame_capture_limit = part.toInt();  // Convert to integer
        }

        part_cnt++;
        // Serial.println(part_cnt);
      }
      // ----------------------------------------------------------------------------------------------------
      if (DEBUG)
      {
        Serial.print("no_of_frame_capture_limit: ");
        Serial.println(no_of_frame_capture_limit);
      }
      // ----------------------------------------------------------------------------------------------------
      writeIntToEEPROM(NO_OF_FRAME_ADDR, no_of_frame_capture_limit);
      read_config_from_eeprom_to_variables();
      // ----------------------------------------------------------------------------------------------------
      size_t bytesSent = client.write(fRameCApLiM.c_str(), fRameCApLiM.length());
  
      if (DEBUG)
        Serial.printf("bytesSent: %d\n", bytesSent);

      if (bytesSent == fRameCApLiM.length())
      {
        if (DEBUG)
          Serial.println("No of Frame reply sent OK");
      }
    }
    // ----------------------------------------------------------------------------------------------------
    else if(server_cmd_buf.indexOf(dElaYhB) >= 0)
    {
      // ----------------------------------------------------------------------------------------------------
      if (DEBUG)
        Serial.println("Server asked to Update HB Delay");
      // ----------------------------------------------------------------------------------------------------
      int startIndex = 0;
      int commaIndex = 0;
      int part_cnt = 0;
      // ----------------------------------------------------------------------------------------------------
      while ((commaIndex = server_cmd_buf.indexOf(',', startIndex)) != -1)
      {
        String part = server_cmd_buf.substring(startIndex, commaIndex);
        // Serial.println(part);
        startIndex = commaIndex + 1;
        // Serial.println(startIndex);
        // Serial.println(commaIndex);
        if (part_cnt == 1)
        {
          hb_delay_cnt = part.toInt();  // Convert to integer
        }

        part_cnt++;
        // Serial.println(part_cnt);
      }
      // ----------------------------------------------------------------------------------------------------
      if (DEBUG)
      {
        Serial.print("hb_delay_cnt: ");
        Serial.println(hb_delay_cnt);
      }
      // ----------------------------------------------------------------------------------------------------
      writeIntToEEPROM(HB_DELAY_ADDR, hb_delay_cnt);
      read_config_from_eeprom_to_variables();
      // ----------------------------------------------------------------------------------------------------
      size_t bytesSent = client.write(dElaYhB.c_str(), dElaYhB.length());
  
      if (DEBUG)
        Serial.printf("bytesSent: %d\n", bytesSent);

      if (bytesSent == dElaYhB.length())
      {
        if (DEBUG)
          Serial.println("HB Delay reply sent OK");
      }
    }
    // ----------------------------------------------------------------------------------------------------
    else if(server_cmd_buf == lgtAlrmChaLu)
    {
      if (DEBUG)
        Serial.println("Server asked for Light & Alarm ON");
      // ----------------------------------------------------------------------------------------------------
      digitalWrite(RELAY_PIN, HIGH);
      size_t bytesSent = client.write(lgtAlrmChaLu.c_str(), lgtAlrmChaLu.length());
  
      if (DEBUG)
        Serial.printf("bytesSent: %d\n", bytesSent);

      if (bytesSent == lgtAlrmChaLu.length())
      {
        if (DEBUG)
          Serial.println("Light & Alarm ON and Reply sent OK");
      }        
    }
    // ----------------------------------------------------------------------------------------------------
    else if(server_cmd_buf == lgtAlrmBOnDhO)
    {
      if (DEBUG)
        Serial.println("Server asked for Light & Alarm OFF");
      // ----------------------------------------------------------------------------------------------------
      digitalWrite(RELAY_PIN, LOW);
      size_t bytesSent = client.write(lgtAlrmBOnDhO.c_str(), lgtAlrmBOnDhO.length());
  
      if (DEBUG)
        Serial.printf("bytesSent: %d\n", bytesSent);

      if (bytesSent == lgtAlrmBOnDhO.length())
      {
        if (DEBUG)
          Serial.println("Light & Alarm OFF and Reply sent OK");
      }
    }
    // ----------------------------------------------------------------------------------------------------
    // If "cApPiC" Text is present in "server_cmd_buf"
    else if(server_cmd_buf.indexOf(cApPiC) >= 0)
    {
      // ----------------------------------------------------------------------------------------------------
      if (DEBUG)
        Serial.println("Server asked for Photo");
      // ----------------------------------------------------------------------------------------------------
      manually_capture_image_and_send_to_server(server_cmd_buf);
    }
    // ----------------------------------------------------------------------------------------------------
    else if(server_cmd_buf.indexOf("CLOSED") >= 0)
    {
      if (DEBUG)
        Serial.println("Connection CLOSED!\nRebooting...");
      
      delay(1000);
      ESP.restart();
    }
  }
  // ====================================================================================================
}
// ***********************************************************************************************

