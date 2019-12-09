#include "epd7in5.h"

int Epd::isSetup = -1;

int Epd::InterfaceSetup(void) {
  if (Epd::isSetup < 0) {
    pinMode(CS_PIN, OUTPUT);
    pinMode(RST_PIN, OUTPUT);
    pinMode(DC_PIN, OUTPUT);
    pinMode(BUSY_PIN, INPUT);

    SPI.begin();
    SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
    Epd::isSetup = 0;
  }
  return Epd::isSetup;
}

void Epd::SpiTransfer(unsigned char data) {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(data);
  digitalWrite(CS_PIN, HIGH);
}
