#include "dataLoader.h"

int DataLoader::Init(String host, int port, String macAddress)
{
    _host = host;
    _port = port;
    _url = "http://" + host + ":" + String(port) + "/";
    _macAddress = macAddress;
}

String DataLoader::getHttpData(String url) {
    String httpData = "";
    Serial.println("[WiFi] URL: " + url);
    if (WiFi.status() == WL_CONNECTED)
    {
        WiFiClient c;
        HTTPClient http;

        if (http.begin(c, url)) {
            // http.setTimeout(500);
            Serial.print("[HTTP] GET");
            int httpCode = http.GET();
            Serial.println(" -> done");

            if (httpCode > 0) {
                if (httpCode == HTTP_CODE_OK) {
                    httpData = http.getString();
                }
            }
            else {
                Serial.println("[HTTP] GET-data not retreived for url : " + url + "[HTTP-CODE: " + String(httpCode) + "]");
            }

            http.end();
        } else  {
            Serial.println("[HTTP] unable to connect to server");
        }
    } else {
        delay(500);
        Serial.println("[WiFi] cannot connect / lost connection");
    }

    return httpData;
}

/*
String DataLoader::postHttpData(String url, String data)
{
    String httpData = "";

    if (WiFi.status() == WL_CONNECTED)
    {
        WiFiClient c;
        HTTPClient http;

        if (http.begin(c, url))
        {
            http.addHeader("Content-Type", "application/x-www-form-urlencoded");
            int httpCode = http.POST(data);
            if (httpCode > 0)
            {
                if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY)
                {
                    httpData = http.getString();
                }
            }
            else
            {
                Serial.println("[HTTP] POST-data not retreived for url : " + url + "[HTTP-CODE: " + String(httpCode) + "]");
            }

            http.end();
        }
        else
        {
            Serial.println("[HTTP] unable to connect to server");
        }
    }
    else
    {
        delay(500);
        Serial.println("[WiFi] cannot connect / lost connection");
    }

    return httpData;
}
*/

String DataLoader::updateData()
{
    return this->getHttpData(_url + "updateData.api?macAddress=" + this->_macAddress);
}

String DataLoader::getBmpData(int segmentsCount, int segmentNumber)
{
    return this->getHttpData(_url + "getBmpData.api?macAddress=" + this->_macAddress + "&segmentsCount=" + String(segmentsCount) + "&segmentNumber=" + String(segmentNumber));
}

int DataLoader::getDelayTime() {
    return this->getHttpData(_url + "getDelayTime.api?macAddress=" + this->_macAddress).toInt();
}

int DataLoader::willReceiveColorData() {
    return this->getHttpData(_url + "willReceiveColorData.api?macAddress=" + this->_macAddress).toInt();
}
