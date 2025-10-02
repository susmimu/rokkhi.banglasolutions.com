// ----------------------------------------------------------------------------------------------------
#include "CloudManager.h"
// ----------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
void connect_to_cloud(void)
{
    DEBUG_PRINT("Connecting to TCP Server ");
    DEBUG_PRINT(serverIP); 
    DEBUG_PRINT(":"); 
    DEBUG_PRINTLN(serverPort);
  // ----------------------------------------------------------------------------------------------------
  if (client.connect(serverIP, serverPort)) 
  {
    DEBUG_PRINTLN("Cloud connection OK");
  }
  else
  {
    DEBUG_PRINTLN("Failed to connect with cloud");
    
    delay(1000);
    ESP.restart();
  }
  // ----------------------------------------------------------------------------------------------------
}
// ***********************************************************************************************


// ***********************************************************************************************
bool login_to_cloud(void)
{
  delay(1000);
  // ----------------------------------------------------------------------------------------------------
  /* Useful Examples of client object:
  Function	                      Description
  --------------------------      ---------------------------------------------------
  client.connect(host, port)	    Connects to a TCP server. Returns true if successful.
  client.connected()	            Returns true if connected, false otherwise.
  client.available()	            Returns the number of bytes available to read.
  client.read()	                  Reads one byte from the server.
  client.readStringUntil(char)	  Reads data from the server until a specific character (e.g., \n).
  client.write(data)	            Sends data to the server.
  client.print(data)	            Sends a string without a newline.
  client.println(data)	          Sends a string with a newline (\r\n).
  client.stop()	                  Closes the connection.
  */
  // ----------------------------------------------------------------------------------------------------
  bool login_success_flag = false;
  String login_packet = device_sl + "," + mac_read;
  String login_reply_buff;
  login_reply_buff.clear();
  // ----------------------------------------------------------------------------------------------------
  // String login_packet_len = String(login_packet.length());
  // Send Login packet to cloud
  if (client.connected())
  {
    // client.println(login_packet);
    client.write(login_packet.c_str(), login_packet.length());
    // delay(100);
    // Dynamic waiting for Cloud Reply
    while (!client.available());
  }
  else
  {
    DEBUG_PRINTLN("Device not connected to Cloud");
    
    delay(1000);
    ESP.restart();
  }
  // ----------------------------------------------------------------------------------------------------


  // ----------------------------------------------------------------------------------------------------
  login_reply_buff = client.readStringUntil('\n');

  DEBUG_PRINT("login_reply_buff: ");
  DEBUG_PRINTLN(login_reply_buff);
  // ----------------------------------------------------------------------------------------------------


  // ----------------------------------------------------------------------------------------------------
  if(login_reply_buff.indexOf("lOgInOK") >= 0)
  {
    login_success_flag = true;

    DEBUG_PRINTLN("Cloud Login Success :)");
    DEBUG_PRINTLN("Triple Flash if Loggedin OK!");
    
    flashLightSignal(3);
  }
  else if(login_reply_buff.indexOf("lOgInERR") >= 0)
  {
    DEBUG_PRINTLN("Cloud Login Auth FAILED :(\nRebooting...");
    delay(1000);
    ESP.restart();
  }
  // ----------------------------------------------------------------------------------------------------
  return login_success_flag;
  // ----------------------------------------------------------------------------------------------------
}
// ***********************************************************************************************


// ***********************************************************************************************
bool sendFlagToServerAndWaitForReply(String flag)
{
  size_t bytesSent = client.write(flag.c_str(), flag.length());
  // ----------------------------------------------------------------------------------------------------
  if (bytesSent == flag.length())
  {
    DEBUG_PRINTLN(flag + " sent OK\nWaiting for Server reply...");
    // ----------------------------------------------------------------------------------------------------
    // Dynamic waiting for Cloud Reply. Max 10 x 1500 = 15 Sec. [.mjpeg -> .mp4 convertion may take long time for long file]
    int dynamic_waiting_cnt = 0;

    while (!client.available())
    {
      delay(10);
      dynamic_waiting_cnt++;

      if (dynamic_waiting_cnt > 1000)
      {
        DEBUG_PRINTLN("No byte received in 10 Sec\Rebooting...");

        ESP.restart();  // If uncommemted below lines will be skipped
        digitalWrite(FLASH_LGT_PIN, LOW);   // OFF Flash Light if somehow ON before
        return false;
      }
    }
    // ----------------------------------------------------------------------------------------------------
    // Something Received from Server
    String server_reply_buf;
    server_reply_buf.clear();
    server_reply_buf = client.readStringUntil('\n');

    DEBUG_PRINTLN("server_reply_buf: " + server_reply_buf);
    // ----------------------------------------------------------------------------------------------------
    if(server_reply_buf.indexOf(flag) >= 0)
    {
      DEBUG_PRINTLN("Server received the Flag: " + flag);
      // ----------------------------------------------------------------------------------------------------
      // If this reply is for HB Copy the reply buffer to a new variable for further processing
      if(server_reply_buf.indexOf("hB") >= 0)
      {
        // FULL reply Text of HB from Server Copy to a String
        full_hb_reply_from_server.clear();
        full_hb_reply_from_server = server_reply_buf;
      }
      else
      {
        full_hb_reply_from_server.clear();
      }
      // ----------------------------------------------------------------------------------------------------
      return true;
    }
  }  
  // ----------------------------------------------------------------------------------------------------
  DEBUG_PRINTLN("Err: 'sendFlagToServerAndWaitForReply'\nRebooting...");
  
  ESP.restart();
}
// ***********************************************************************************************
