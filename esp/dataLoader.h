#include <stdlib.h>
#include <arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#ifndef DATALOADER_H
#define DATALOADER_H

class DataLoader
{
public:
    int Init(String host, int port, String macAddress);

    String getBmpData(int segmentsCount, int segmentNumber);

    String updateData();

    int getDelayTime();

    int willReceiveColorData();

private:

    String getHttpData(String url);

    // String postHttpData(String url, String data);

    String _host;

    int _port;

    String _url;

    String _macAddress;
};

#endif /* DATALOADER_H */
