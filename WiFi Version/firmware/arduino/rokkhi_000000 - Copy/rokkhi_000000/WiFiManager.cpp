// ----------------------------------------------------------------------------------------------------
#include "WiFiManager.h"
// ----------------------------------------------------------------------------------------------------
// Define WiFiClient globally
WiFiClient client;
WebServer server(80);
// ----------------------------------------------------------------------------------------------------
String SSID = "";       // Define the variables (initialize here)
String PASSWORD = "";   // Define the variables (initialize here)
// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
bool connectToWiFi()
{
  int wifi_conn_try_cnt = 0;
  // ----------------------------------------------------------------------------------------------------
  if (DEBUG)
  {
    Serial.println("SSID from EEPROM: " + SSID);
    Serial.println("PASSWORD from EEPROM: " + PASSWORD);
  }
  // ----------------------------------------------------------------------------------------------------
  WiFi.begin(SSID.c_str(), PASSWORD.c_str());

  if (DEBUG)
    Serial.print("Connecting to WiFi");
  // ----------------------------------------------------------------------------------------------------
  while (WiFi.status() != WL_CONNECTED) 
  {
    if (DEBUG)
      Serial.print(".");

    delay(1000);
    wifi_conn_try_cnt++;
    // ----------------------------------------------------------------------------------------------------
    if (wifi_conn_try_cnt > 30)
    {
      if (DEBUG)
        Serial.println("\nTried 30 Seconds to connect with WiFi but Failed :(\nCreating AP Mode");

      return false;
    }
  }
  // ----------------------------------------------------------------------------------------------------
  if (DEBUG)
  {
    Serial.println("\nConnected to WiFi: " + SSID);
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  }

  if (DEBUG)
    Serial.println("Double Flash if Connected to WiFi!");

  flashLightSignal(2);

  return true;
  // ----------------------------------------------------------------------------------------------------
}
// ***********************************************************************************************


// ***********************************************************************************************
// Start ESP32 in AP mode
void startAPMode()
{
  WiFi.softAP("Rokkhi", "42316237");

  if (DEBUG)
  {
    Serial.println("ESP32 in AP Mode - Connect to 'Rokkhi' and go to 192.168.4.1");
  }  

  server.on("/", handleRoot);
  server.on("/save", HTTP_POST, handleSave);
  server.begin();
}
// ***********************************************************************************************


// ***********************************************************************************************
// Web Page to Enter SSID & Password
void handleRoot() 
{
  server.send(200, "text/html", R"rawliteral(
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Centered Div</title>
          <style>
            body 
            {
              display: flex;
              justify-content: center;
              align-items: center;
              height: 100vh;
              margin: 0;
              background-color: #f0f0f0;
            }

            .center-box 
            {
              width: auto;
              height: auto;
              background-color: #4CAF50;
              color: white;
              display: flex;
              justify-content: center;
              align-items: center;
              font-size: 20px;
              border-radius: 5px;
              padding-left: 15px;
              padding-right: 15px;
            }
          </style>
        </head>
        
        <body>
          <div class="center-box">
            <form action="/save" method="POST">
              <h3 style="text-align: center; margin-top: 15; margin-bottom: 10;">Enter WiFi Details</h3>
              <hr>
              
              WiFi Name: <input type="text" name="ssid"><br>
              Password: <input style="margin-left:15px;" type="text" name="password"><br>
              
              <h6 style="text-align: end; padding: 0; margin-top: 10px; margin-bottom: 0px;">
                <input style="padding: 5px;" type="submit" value="Save & Connect">
              </h6>
            </form>
          </div>
        </body>
      </html>
  )rawliteral");
}
// ***********************************************************************************************


// ***********************************************************************************************
// Save SSID & Password to EEPROM
void handleSave() 
{
  String newSSID = server.arg("ssid");
  String newPassword = server.arg("password");
  
  newSSID.trim();       // from HTML form and Removes leading/trailing spaces)
  newPassword.trim();   // from HTML form and Removes leading/trailing spaces)

  if (DEBUG)
  {
    Serial.println("newSSID >>>>>>>: " + newSSID);
    Serial.println("newPassword >>>: " + newPassword);
  }
  // ----------------------------------------------------------------------------------------------------
  if(newSSID.length() == 0 || newPassword.length() == 0)
  {
    server.send(200, "text/html", R"rawliteral(
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Centered Div</title>
            <style>
              body 
              {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;;
              }

              .center-box 
              {
                width: auto;
                height: auto;
                background-color: red;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 15px;
                border-radius: 5px;
                padding-left: 15px;
                padding-right: 15px;
              }
            </style>
          </head>
          
          <body>
            <div class="center-box">
              <h3 style="text-align: center;">WiFi Name or Password is Empty!</h3>
            </div>
          </body>
        </html>
    )rawliteral");  
  }
  // ----------------------------------------------------------------------------------------------------
  else
  {
    // ----------------------------------------------------------------------------------------------------
    // initEEPROM();
    // eraseAllEEPROMData();
    // deinitEEPROM();
    // ----------------------------------------------------------------------------------------------------
    writeStringToEEPROM(SSID_ADDR, newSSID);

    if (DEBUG)
      Serial.println("WiFi SSID saved!");
    // ----------------------------------------------------------------------------------------------------
    writeStringToEEPROM(PASS_ADDR, newPassword);

    if (DEBUG)
      Serial.println("WiFi PASSWORD saved!");
    // ----------------------------------------------------------------------------------------------------
    server.send(200, "text/html", R"rawliteral(
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Centered Div</title>
            <style>
              body 
              {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
              }

              .center-box 
              {
                width: auto;
                height: auto;
                background-color: #4CAF50;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 15px;
                border-radius: 5px;
                padding-left: 15px;
                padding-right: 15px;
              }
            </style>
          </head>
          
          <body>
            <div class="center-box">
              <h3 style="text-align: center;">WiFi Name and Password Saved! Restarting...</h3>
            </div>
          </body>
        </html>
    )rawliteral");

    delay(1000);
    ESP.restart();
  }
}
// ***********************************************************************************************
