// ----------------------------------------------------------------------------------------------------
#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H
// ----------------------------------------------------------------------------------------------------
#include <WiFi.h>
#include <WebServer.h>
#include "CommonConfig.h"
#include "EEPROMManager.h"
// ----------------------------------------------------------------------------------------------------
extern String SSID;             // Declare the variable (no initialization)
extern String PASSWORD;         // Declare the variable (no initialization)
// ----------------------------------------------------------------------------------------------------
extern WebServer server;
// Declare WiFiClient as extern
extern WiFiClient client;
/* Useful Examples of client object:
Function	                      Description
--------------------------      ---------------------------------------------------
client.connect(host, port)	    Connects to a TCP server (returns true if successful).
client.connected()	            Checks if ESP32 is still connected to the server.
client.available()	            Checks if data is available to read from the server.
client.read()	                  Reads one byte from the server.
client.read(buffer, length)	    Reads multiple bytes into a buffer.
client.readString()	            Reads the incoming data as a String.
client.readStringUntil(char)	  Reads data from the server until a specific character (e.g., \n).
client.write(data)	            Sends data to the server.
client.write("text")	          Send a string.
client.write(buffer, size)	    Send multiple bytes.
client.write(uint8_t byte)	    Send a single byte.
client.println(data)	          Sends data with a newline (\n) at the end.
client.print(data)	            Sends data without a newline.
client.flush()	                Waits for outgoing data to be sent.
client.stop()	                  Disconnects from the server.
client.remoteIP()	              Returns the server’s IP address.
client.remotePort()	            Returns the server’s port number.
*/
// ----------------------------------------------------------------------------------------------------


// ----------------------------------------------------------------------------------------------------
// Function prototypes
bool connectToWiFi();
void startAPMode();
void handleRoot();
void handleSave();



// ----------------------------------------------------------------------------------------------------
#endif
// ----------------------------------------------------------------------------------------------------
