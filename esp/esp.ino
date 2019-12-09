#include <ESP8266WiFi.h>
#include <arduino.h>

#include "epd7in5.h"
#include "dataLoader.h"

const char *ssid = "MAX!Box 7560 WU";
const char *password = "37090722270364141496";

IPAddress myIP;
String macAddress;
Epd *epd;
DataLoader *dl;
bool colorData = false;

void setup()
{
  // Start serial connection at 115200 Baud
  Serial.begin(115200);

  // Connect to Wifi
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  // DEBUG: print IP over Serial
  Serial.println("");
  Serial.print("IP address: ");
  Serial.println(myIP = WiFi.localIP());
  Serial.print("Mac: ");
  Serial.println(macAddress = WiFi.macAddress());

  // Create screen (EPD) instance
  epd = new Epd();
  // // Initialize / Startup screen
  // if (epd->Init() < 0)
  // {
  //   Serial.print("[EPD] e-Paper init failed");
  //   return;
  // }
  // // Reset / Flush screen
  // epd->FrameDataStart();
  // epd->FrameDataFlush();
  // epd->FrameDataStop();
  // epd->FrameDataShow();

  Serial.println("[STATUS] reset/restart done");

  // Initialize data loader
  dl = new DataLoader();
  // Name this board "Frame1_BW"
  dl->Init("192.168.5.241", 8080, macAddress);
  // // Pass the size of the screen to data loader
  // dl->setScreenInfo(EPD_HEIGHT, EPD_WIDTH);
  // // Pass the size and position of frame to loader
  // dl->setFrameInfo(49, 15, 544, 349);
  Serial.print("[STATUS] SENT DATA");

  colorData = dl->willReceiveColorData() > 0;
}

void loop()
{
  // Initialize / Startup screen
  if (epd->Init() < 0)
  {
    Serial.print("[EPD] e-Paper init failed");
    return;
  }
  dl->updateData();

  epd->FrameDataStart();
  int segments = 4;
  int segmentCount = 0;
  while (segmentCount < segments)
  {
    String data = dl->getBmpData(segments, segmentCount);
    Serial.println("[STATUS] segment (i.e. BMP) data length: " + String(data.length()));
    if (data.length() > 0) {
      epd->FrameDataBMP(data, colorData);
      segmentCount++;
    } else {
      Serial.println("[STATUS] did not update segment " + String(segmentCount) + " out of " + String(segments) + " segments");
    } 
  }

  epd->FrameDataStop();
  epd->FrameDataShow();

  Serial.println("[STATUS] Startup screen loading done");

  int delayTime = dl->getDelayTime();
  Serial.println("[STATUS] waiting " + String(delayTime));
  delay(delayTime);
}
