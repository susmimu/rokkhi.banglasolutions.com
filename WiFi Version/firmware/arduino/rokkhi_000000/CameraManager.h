// ----------------------------------------------------------------------------------------------------
/*
Yes, if you want to change the camera_config at runtime, you need to:
1. Deinitialize the camera using esp_camera_deinit();
2. Modify the camera_config parameters
3. Reinitialize the camera using esp_camera_init(&camera_config);
----------------------------------------------------------------------------------------------------
The image format can be one of the following options:
PIXFORMAT_YUV422
PIXFORMAT_GRAYSCALE
PIXFORMAT_RGB565
PIXFORMAT_JPEG
----------------------------------------------------------------------------------------------------
FRAMESIZE_96X96,    // 96x96
FRAMESIZE_QQVGA,    // 160x120
FRAMESIZE_128X128,  // 128x128
FRAMESIZE_QCIF,     // 176x144
FRAMESIZE_HQVGA,    // 240x176
FRAMESIZE_240X240,  // 240x240
FRAMESIZE_QVGA,     // 320x240
FRAMESIZE_320X320,  // 320x320
FRAMESIZE_CIF,      // 400x296
FRAMESIZE_HVGA,     // 480x320
FRAMESIZE_VGA,      // 640x480
FRAMESIZE_SVGA,     // 800x600
FRAMESIZE_XGA,      // 1024x768
FRAMESIZE_HD,       // 1280x720
FRAMESIZE_SXGA,     // 1280x1024
FRAMESIZE_UXGA,     // 1600x1200
// 3MP Sensors
FRAMESIZE_FHD,      // 1920x1080
FRAMESIZE_P_HD,     //  720x1280
FRAMESIZE_P_3MP,    //  864x1536
FRAMESIZE_QXGA,     // 2048x1536
// 5MP Sensors
FRAMESIZE_QHD,      // 2560x1440
FRAMESIZE_WQXGA,    // 2560x1600
FRAMESIZE_P_FHD,    // 1080x1920
FRAMESIZE_QSXGA,    // 2560x1920
FRAMESIZE_5MP,      // 2592x1944
FRAMESIZE_INVALID
----------------------------------------------------------------------------------------------------
sensor_t * s = esp_camera_sensor_get();
s->set_brightness(s, 0);     // -2 to 2
s->set_contrast(s, 0);       // -2 to 2
s->set_saturation(s, 0);     // -2 to 2
s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
s->set_aec2(s, 0);           // 0 = disable , 1 = enable
s->set_ae_level(s, 0);       // -2 to 2
s->set_aec_value(s, 300);    // 0 to 1200
s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
s->set_agc_gain(s, 0);       // 0 to 30
s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
s->set_bpc(s, 0);            // 0 = disable , 1 = enable
s->set_wpc(s, 1);            // 0 = disable , 1 = enable
s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
s->set_lenc(s, 1);           // 0 = disable , 1 = enable
s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
s->set_vflip(s, 0);          // 0 = disable , 1 = enable
s->set_dcw(s, 1);            // 0 = disable , 1 = enable
s->set_colorbar(s, 0);       // 0 = disable , 1 = enable
*/ 
// ----------------------------------------------------------------------------------------------------
#ifndef CAMERA_MANAGER_H
#define CAMERA_MANAGER_H
// ----------------------------------------------------------------------------------------------------
#include <Arduino.h>
#include "esp_camera.h"
#include "CommonConfig.h"
#include "SDManager.h"
#include "CloudManager.h"
// ----------------------------------------------------------------------------------------------------
// ESP32-CAM Pin Definitions
// CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
// ----------------------------------------------------------------------------------------------------
// Motion Detection Parameters
#define ROI_X                 40  // ROI X Start Position
#define ROI_Y                 30  // ROI Y Start Position
#define ROI_W                 80  // ROI Width
#define ROI_H                 60  // ROI Height
#define SAMPLE_STEP          100  // How many bytes to skip (increase for faster but less accurate detection)

#define PIX_DIFF_THRESHOLD    30  // Pixel intensity difference threshold
#define MOTION_PERCENTAGE      5  // % of pixels that must change to trigger motion
// ----------------------------------------------------------------------------------------------------
extern camera_config_t camera_config;
// ----------------------------------------------------------------------------------------------------
// Function prototypes
void initializeCameraWithParams(pixformat_t pixel_format, framesize_t frame_size, int hmirror, int vflip);
// void captureMotionPhotoToGlobalBuff(bool extraFlash);
void manually_capture_image_and_send_to_server(String img_params);


// ----------------------------------------------------------------------------------------------------
#endif
// ----------------------------------------------------------------------------------------------------
