// ----------------------------------------------------------------------------------------------------
#include "CloudManager.h"
// ----------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------


// ***********************************************************************************************
void connect_to_cloud(void)
{
  if (DEBUG)
  {
    Serial.print("Connecting to TCP Server ");
    Serial.print(serverIP); 
    Serial.print(":"); 
    Serial.println(serverPort);
  }  
  // ----------------------------------------------------------------------------------------------------
  if (client.connect(serverIP, serverPort)) 
  {
    if (DEBUG)
    {
      Serial.println("Cloud connection OK");
    }
  }
  else
  {
    if (DEBUG)
    {
      Serial.println("Failed to connect with cloud");
    }
    
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
    if (DEBUG)
    {
      Serial.println("Device not connected to Cloud");
    }
    
    delay(1000);
    ESP.restart();
  }
  // ----------------------------------------------------------------------------------------------------


  // ----------------------------------------------------------------------------------------------------
  login_reply_buff = client.readStringUntil('\n');

  if (DEBUG)
  {
    Serial.print("login_reply_buff: ");
    Serial.println(login_reply_buff);
  }
  // ----------------------------------------------------------------------------------------------------


  // ----------------------------------------------------------------------------------------------------
  if(login_reply_buff.indexOf("lOgInOK") >= 0)
  {
    login_success_flag = true;

    if (DEBUG)
      Serial.println("Cloud Login Success :)");

    if (DEBUG)
      Serial.println("Triple Flash if Loggedin OK!");

    flashLightSignal(3);
  }
  else if(login_reply_buff.indexOf("lOgInERR") >= 0)
  {
    if (DEBUG)
      Serial.println("Cloud Login Auth FAILED :(\nRebooting...");
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
    if (DEBUG)
      Serial.println(flag + " sent OK\nWaiting for Server reply...");
    // ----------------------------------------------------------------------------------------------------
    // Dynamic waiting for Cloud Reply. Max 10 x 1000 = 10 Sec.
    int dynamic_waiting_cnt = 0;

    while (!client.available())
    {
      delay(10);
      dynamic_waiting_cnt++;

      if (dynamic_waiting_cnt > 1000)
      {
        if (DEBUG)
          Serial.println("No byte received in 10 Sec\Rebooting...");

        ESP.restart();
      }
    }
    // ----------------------------------------------------------------------------------------------------
    // Something Received from Server
    String server_reply_buf;
    server_reply_buf.clear();
    server_reply_buf = client.readStringUntil('\n');

    if (DEBUG)
      Serial.println("server_reply_buf: " + server_reply_buf);
    // ----------------------------------------------------------------------------------------------------
    if(server_reply_buf.indexOf(flag) >= 0)
    {
      if (DEBUG)
        Serial.println("Server received the Flag: " + flag);

      return true;
    }
  }  
  // ----------------------------------------------------------------------------------------------------
  if (DEBUG)
    Serial.println("Err: 'sendFlagToServerAndWaitForReply'\nRebooting...");
  
  ESP.restart();
}
// ***********************************************************************************************
