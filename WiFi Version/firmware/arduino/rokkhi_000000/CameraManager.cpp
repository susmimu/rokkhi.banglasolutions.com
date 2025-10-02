// ----------------------------------------------------------------------------------------------------
#include "CameraManager.h"
// ----------------------------------------------------------------------------------------------------
camera_config_t camera_config;
// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
void initializeCameraWithParams(pixformat_t pixel_format, framesize_t frame_size, int hmirror, int vflip)
{
  // ----------------------------------------------------------------------------------------------------
  camera_config.ledc_channel = LEDC_CHANNEL_0;
  camera_config.ledc_timer   = LEDC_TIMER_0;
  camera_config.pin_d0       = Y2_GPIO_NUM;
  camera_config.pin_d1       = Y3_GPIO_NUM;
  camera_config.pin_d2       = Y4_GPIO_NUM;
  camera_config.pin_d3       = Y5_GPIO_NUM;
  camera_config.pin_d4       = Y6_GPIO_NUM;
  camera_config.pin_d5       = Y7_GPIO_NUM;
  camera_config.pin_d6       = Y8_GPIO_NUM;
  camera_config.pin_d7       = Y9_GPIO_NUM;
  camera_config.pin_xclk     = XCLK_GPIO_NUM;
  camera_config.pin_pclk     = PCLK_GPIO_NUM;
  camera_config.pin_vsync    = VSYNC_GPIO_NUM;
  camera_config.pin_href     = HREF_GPIO_NUM;
  camera_config.pin_sscb_sda = SIOD_GPIO_NUM;
  camera_config.pin_sscb_scl = SIOC_GPIO_NUM;
  camera_config.pin_pwdn     = PWDN_GPIO_NUM;
  camera_config.pin_reset    = RESET_GPIO_NUM;
  camera_config.xclk_freq_hz = 20000000;
  camera_config.pixel_format = pixel_format; // GRAYSCALE
  // ----------------------------------------------------------------------------------------------------
  // init with high specs to pre-allocate larger buffers
  if(psramFound())
  {
    camera_config.frame_size = frame_size;  // 800x600
    camera_config.jpeg_quality = 10;        // 10-63 lower number means higher quality
    camera_config.fb_count = 2;
  } 
  else 
  {
    camera_config.frame_size = FRAMESIZE_HVGA,  // 480x320
    camera_config.jpeg_quality = 12;            // 10-63 lower number means higher quality
    camera_config.fb_count = 1;
  }
  // ----------------------------------------------------------------------------------------------------
  // // NO NEED to DeInit camera. It is unnecessary for the first time
  // // Camera Deinit Here.
  // esp_err_t err_di = esp_camera_deinit();
  
  // if (err_di != ESP_OK) 
  // {
  //   if (DEBUG)
  //     Serial.printf("Camera Deinit failed with error: 0x%x\n", err_di);

  //   // delay(1000);
  //   // ESP.restart();
  // }
  // ----------------------------------------------------------------------------------------------------
  // Init the camera using configs.
  esp_err_t err_i = esp_camera_init(&camera_config);

  if (err_i != ESP_OK) 
  {
    DEBUG_PRINT("Camera Init FAILED with error:");
    DEBUG_PRINTLN(err_i);
    
    ESP.restart();
  }
  else
  {
    DEBUG_PRINTLN("Camera init SUCCESS!");
  }

  delay(500);
  // ----------------------------------------------------------------------------------------------------  
  
  // ----------------------------------------------------------------------------------------------------
  // // After initializing the camera, use esp_camera_sensor_get() to access the camera sensor and modify settings.
  // sensor_t *s = esp_camera_sensor_get();  // Get camera sensor
  // // ----------------------------------------------------------------------------------------------------
  // // ✅ Change Horizontal Mirror
  // s->set_hmirror(s, hmirror);
  // // ----------------------------------------------------------------------------------------------------
  // // ✅ Change Vertical Flip
  // s->set_vflip(s, vflip);
  // // ----------------------------------------------------------------------------------------------------
  // if (DEBUG)
  //   Serial.println("✅ Camera settings updated!");
  // // ----------------------------------------------------------------------------------------------------
  // delay(100);
  // ----------------------------------------------------------------------------------------------------
  // // Capture some dummy images for stability
  // for (int i = 0; i < 5; i++)
  // {
  //   fb = esp_camera_fb_get();

  //   if (fb)
  //   {
  //     if (DEBUG)
  //       Serial.printf("Dummy image captured OK! Size: %d bytes\n", fb->len);

  //     esp_camera_fb_return(fb);  // Return the frame buffer to clear memory      
  //   }
  //   else
  //   {
  //     if (DEBUG)      
  //       Serial.printf("Dummy image capture FAILED: %d\n", i);
  //   }

  //   delay(10);
  // }
  // ----------------------------------------------------------------------------------------------------
  // // Clear Global Buffer if it has any old Image Data
  // if(fb)
  // {
  //   fb = NULL;

  //   if (DEBUG)      
  //     Serial.println("fb Global Buffer CLEARED");
  // }
  // // ----------------------------------------------------------------------------------------------------
  // delay(100);
}
// ***********************************************************************************************


// // ***********************************************************************************************
// void captureMotionPhotoToGlobalBuff(bool extraFlash)
// {
//   // ----------------------------------------------------------------------------------------------------
//   if (DEBUG)
//   {
//     Serial.print("extraFlash: ");
//     Serial.println(extraFlash);
//   }
//   // ----------------------------------------------------------------------------------------------------
//   if (extraFlash)
//   {
//     digitalWrite(FLASH_LGT_PIN, HIGH);

//     if (DEBUG)
//     {
//       Serial.println("Flash Light ON");
//     }

//     delay(50);
//   }
//   else
//   {
//     digitalWrite(FLASH_LGT_PIN, LOW);

//     if (DEBUG)
//     {
//       Serial.println("Flash Light OFF");
//     }
//   }
//   // ----------------------------------------------------------------------------------------------------
//   // Capture some images for stability
//   for (int i = 0; i < 3; i++)
//   {
//     fb = esp_camera_fb_get();

//     if (fb) 
//     {
//       if (DEBUG)
//         Serial.printf("Some captured OK! Size: %d bytes\n", fb->len);

//       esp_camera_fb_return(fb);  // Return the frame buffer to clear memory      
//     }
//     else
//     {
//       if (DEBUG)      
//         Serial.printf("Some capture FAILED: %d\n", i);
//     }

//     delay(5);
//   }
//   // After breaking the loop
//   delay(100);
//   // ----------------------------------------------------------------------------------------------------
//   // Clear Global Buffer if it has any old Image Data
//   if(fb)
//   {
//     esp_camera_fb_return(fb);

//     if (DEBUG)      
//       Serial.println("fb Global Buffer CLEARED");
//   }
//   // ----------------------------------------------------------------------------------------------------
//   // Now Capture Actual Motion Photo
//   fb = esp_camera_fb_get();

//   if (DEBUG)
//     Serial.println("Motion Photo Captured in 'fb' Buffer!");
//   // ----------------------------------------------------------------------------------------------------
//   if (extraFlash)
//   {
//     digitalWrite(FLASH_LGT_PIN, LOW);

//     if (DEBUG)
//     {
//       Serial.println("Flash Light OFF");
//     }
//   }
// }
// // ***********************************************************************************************


// ***********************************************************************************************
void manually_capture_image_and_send_to_server(String img_params)
{
  // ----------------------------------------------------------------------------------------------------
  DEBUG_PRINT("img_params: ");
  DEBUG_PRINTLN(img_params);
  
  int startIndex   = 0;
  int commaIndex   = 0;

  int requested_frame_size;
  int requested_jpeg_quality;
  int requested_extra_flash;
  // ----------------------------------------------------------------------------------------------------
  int part_cnt = 0;

  while ((commaIndex = img_params.indexOf(',', startIndex)) != -1)
  {
    // ----------------------------------------------------------------------------------------------------
    String part = img_params.substring(startIndex, commaIndex);
    // DEBUG_PRINTLN(part);
    startIndex = commaIndex + 1;
    // DEBUG_PRINTLN(startIndex);
    // DEBUG_PRINTLN(commaIndex);
    if (part_cnt == 2)
    {
      requested_frame_size = part.toInt();
    }
    else if (part_cnt == 3)
    {
      requested_jpeg_quality = part.toInt();
    }
    else if (part_cnt == 4)
    {
      requested_extra_flash = part.toInt();
    }

    part_cnt++;
  }
  // ----------------------------------------------------------------------------------------------------
  DEBUG_PRINT("requested_frame_size: ");
  DEBUG_PRINTLN(requested_frame_size);
  DEBUG_PRINT("requested_jpeg_quality: ");
  DEBUG_PRINTLN(requested_jpeg_quality);
  DEBUG_PRINT("requested_extra_flash: ");
  DEBUG_PRINTLN(requested_extra_flash);
  // ----------------------------------------------------------------------------------------------------
  framesize_t frame_size = FRAMESIZE_QQVGA;   // 160x120

  switch (requested_frame_size) 
  {
    case 0:
      frame_size = FRAMESIZE_QQVGA;   // 160x120
      break;
    case 1:
      frame_size = FRAMESIZE_QCIF;   // 176x144
      break;
    case 2:
      frame_size = FRAMESIZE_HQVGA;   // 240x176
      break;
    case 3:
      frame_size = FRAMESIZE_QVGA;   // 320x240
      break;
    case 4:
      frame_size = FRAMESIZE_CIF;   // 400x296
      break;
    case 5:
      frame_size = FRAMESIZE_VGA;   // 640x480
      break;
    case 6:
      frame_size = FRAMESIZE_SVGA;   // 800x600
      break;
    case 7:
      frame_size = FRAMESIZE_XGA;   // 1024x768 
      break;
    case 8:
      frame_size = FRAMESIZE_HD;   // 1280x720 
      break;
    case 9:
      frame_size = FRAMESIZE_SXGA;   // 1280x1024
      break;
    case 10:
      frame_size = FRAMESIZE_UXGA;   // 1600x1200
      break;
    default:
      frame_size = FRAMESIZE_QQVGA;   // 160x120
  }
  // ----------------------------------------------------------------------------------------------------
  // // Resolution is fixed to 800x600 OR 640x480. So, NO NEED to Init/ Denit Cam. Frequent Change create isse
  // camera_config.frame_size = frame_size;
  // // delay(1000);
  // ----------------------------------------------------------------------------------------------------
  // // Camera deinit
  // esp_err_t err_di = esp_camera_deinit();
  
  // if (err_di != ESP_OK) 
  // {
  //   if (DEBUG)
  //     Serial.printf("Camera Deinit failed with error 0x%x", err_di);

  //   // delay(1000);
  //   // ESP.restart();
  // }
  // ----------------------------------------------------------------------------------------------------
  // // Camera Init
  // esp_err_t err_i = esp_camera_init(&camera_config);
  // // Get camera sensor settings
  // sensor_t *s = esp_camera_sensor_get();
  // // If you need to rotate the image 180°, use both functions:
  // // Set image flipping/mirroring
  // s->set_hmirror(s, 1);  // Flip left-right
  // s->set_vflip(s, 1);    // Flip top-bottom (180° rotation)  
  // delay(5);
  
  // if (err_i != ESP_OK) 
  // {
  //   if (DEBUG)
  //     Serial.printf("Camera init FAILED with error 0x%x\nRebooting...\n", err_i);

  //   delay(1000);
  //   ESP.restart();
  // }
  // else
  // {
  //   if (DEBUG)
  //     Serial.println("Camera init SUCCESS!");

  //   delay(5);
  // }
  // ----------------------------------------------------------------------------------------------------

  // ----------------------------------------------------------------------------------------------------
  if (requested_extra_flash == 1)
  {
    DEBUG_PRINTLN("Turning ON Flash...");
    digitalWrite(FLASH_LGT_PIN, HIGH);
    delay(100);
  }
  else
  {
    DEBUG_PRINTLN("Turning OFF Flash...");
    digitalWrite(FLASH_LGT_PIN, LOW);
  }
  // ----------------------------------------------------------------------------------------------------

  // ----------------------------------------------------------------------------------------------------
  // Capture Some dummy Images for stability
  for (int i = 0; i < 10; i++)
  {
    fb = esp_camera_fb_get();

    if (fb) 
    {
      DEBUG_PRINT("Some captured OK! Size: ");
      DEBUG_PRINTLN(fb->len);

      esp_camera_fb_return(fb);  // Return the frame buffer to clear memory      
    }
    else
    {
      DEBUG_PRINT("Some captured FAILED: ");
      DEBUG_PRINTLN(i);
    }

    delay(10);
  }
  // ----------------------------------------------------------------------------------------------------
  delay(100);
  // After breaking the loop, Clear Global Buffer if it has any old Image Data
  if(fb)
  {
    esp_camera_fb_return(fb);
    DEBUG_PRINTLN("fb Global Buffer CLEARED");
  }
  // ----------------------------------------------------------------------------------------------------

  // ----------------------------------------------------------------------------------------------------
  // Now Capture Actual Photo
  fb = esp_camera_fb_get();

  if(fb)
  {
    DEBUG_PRINTLN("Photo Captured in 'fb' Buffer!");
  }
  else
  {
    DEBUG_PRINTLN("Image capture failed :(");

    // delay(1000);
    // ESP.restart();
  }
  // ----------------------------------------------------------------------------------------------------

  // ----------------------------------------------------------------------------------------------------
  digitalWrite(FLASH_LGT_PIN, LOW);
  DEBUG_PRINTLN("Extra Flash Light OFF"); 
  // ----------------------------------------------------------------------------------------------------

  // ----------------------------------------------------------------------------------------------------
  // Now Sending Image to the server
  if (fb)
  {
    DEBUG_PRINTLN("Telling Server to Save Images and\nWaiting for response...");
    // ----------------------------------------------------------------------------------------------------
    if (sendFlagToServerAndWaitForReply("CaPpIcStrt"))
    {
      DEBUG_PRINTLN("Server successfully informed for 'CaPpIcStrt'");
    }
    // ----------------------------------------------------------------------------------------------------
    // Server already Confirmed now can send Images
    client.write((uint8_t*)&fb->len, 4);  // Send Size
    delay(10);
    client.write(fb->buf, fb->len);       // Send Data    
    // ----------------------------------------------------------------------------------------------------
    esp_camera_fb_return(fb);

    DEBUG_PRINTLN("FULL Image Sent!\nfb Global Buffer CLEARED");
  }
}
// ***********************************************************************************************
