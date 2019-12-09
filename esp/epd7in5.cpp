#include "epd7in5.h"

int Epd::Init(void) {
  if (Epd::InterfaceSetup() < 0) {
    return -1;
  }
  Reset();

  SendCommand(POWER_SETTING);
  SendData(0x37);
  SendData(0x00);

  SendCommand(PANEL_SETTING);
  SendData(0xCF);
  SendData(0x08);

  SendCommand(BOOSTER_SOFT_START);
  SendData(0xc7);
  SendData(0xcc);
  SendData(0x28);

  SendCommand(POWER_ON);
  WaitUntilIdle();

  SendCommand(PLL_CONTROL);
  SendData(0x3c);

  SendCommand(TEMPERATURE_CALIBRATION);
  SendData(0x00);

  SendCommand(VCOM_AND_DATA_INTERVAL_SETTING);
  SendData(0x77);

  SendCommand(TCON_SETTING);
  SendData(0x22);

  SendCommand(TCON_RESOLUTION);
  SendData(0x02);     //source 640
  SendData(0x80);
  SendData(0x01);     //gate 384
  SendData(0x80);

  SendCommand(VCM_DC_SETTING);
  SendData(0x1e);      //decide by LUT file

  SendCommand(FLASH_MODE);
  SendData(0x03);

  return 0;
}

void Epd::WaitUntilIdle(void) {
  while (digitalRead(BUSY_PIN) == 0) {     //0: busy, 1: idle
    delay(100);
  }
}

void Epd::Reset(void) {
  digitalWrite(RST_PIN, LOW);                //module reset
  delay(200);
  digitalWrite(RST_PIN, HIGH);
  delay(200);
}

// void SetLut(void);
// void DisplayFrame(const unsigned char* frame_buffer);

void Epd::FrameDataStart(void) {
  SendCommand(0x10);
}

/**
   receives a String encoding the bit-data as hex.
   e.g.:   0A = 0x00000101
   which translates into 8 colors for 8 pixels like so:
   0x0A --> 0b00000101
   [b0] 0 --> 0b0000
   [b1] 0 --> 0b0000
   [b2] 0 --> 0b0000
   [b3] 0 --> 0b0000
   [b4] 0 --> 0b0000
   [b5] 0 --> 0b0011
   [b6] 0 --> 0b0000
   [b7] 0 --> 0b0011

*/
void Epd::FrameDataHexLine(String lineData) {
  // Stop if less than 640 bits (i.e. 80 bit) are to be displayed
  // Here, the string is Hex formatted, so 2 chars per byte
  if (lineData.length() == 0 || lineData.length() < EPD_WIDTH >> 2 || lineData.length() % (EPD_WIDTH >> 2) != 0) {
    return;
  }

  const char* dataPtr = lineData.c_str();
  char data = 0x00;

  for (int x = 0; x < lineData.length(); x++) {
    char ch = dataPtr[x];

    if (ch >= '0' && ch <= '9')
      ch = ch - '0';
    if (ch >= 'A' && ch <= 'F')
      ch = ch - 'A' + 10;
    if (ch >= 'a' && ch <= 'f')
      ch = ch - 'a' + 10;

    for (int i = 3; i >= 0; i--) {
      if (i % 2 == 0) {
        data |= ((ch >> i) & 0x01 == 0x01) ? 0x03 : 0x00;
        SendData(data);
      } else {
        data = ((ch >> i) & 0x01 == 0x01) ? 0x30 : 0x00;
      }
    }
  }
}

void Epd::FrameDataBMP(String bmpData, bool colorData) {
  const char* dataPtr = bmpData.c_str();
  char data = 0x00;
  int length = bmpData.length();

  if (colorData) {
    for (int x = 0; x < length; x++) {
      char ch = dataPtr[x];
      switch (ch)
      {
      case '0': SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      case '1': SendData(COLOR_BLACK << 4 | COLOR_RED); break;
      case '2': SendData(COLOR_BLACK << 4 | COLOR_RED); break;
      case '3': SendData(COLOR_BLACK << 4 | COLOR_WHITE); break;
      case '4': SendData(COLOR_RED   << 4 | COLOR_BLACK); break;
      case '5': SendData(COLOR_RED   << 4 | COLOR_RED); break;
      case '6': SendData(COLOR_RED   << 4 | COLOR_RED); break;
      case '7': SendData(COLOR_RED   << 4 | COLOR_WHITE); break;
      case '8': SendData(COLOR_RED   << 4 | COLOR_BLACK); break;
      case '9': SendData(COLOR_RED   << 4 | COLOR_RED); break;
      case 'a': SendData(COLOR_RED   << 4 | COLOR_RED); break;
      case 'b': SendData(COLOR_RED   << 4 | COLOR_WHITE); break;
      case 'c': SendData(COLOR_WHITE << 4 | COLOR_BLACK); break;
      case 'd': SendData(COLOR_WHITE << 4 | COLOR_RED); break;
      case 'e': SendData(COLOR_WHITE << 4 | COLOR_RED); break;
      case 'f': SendData(COLOR_WHITE << 4 | COLOR_WHITE); break;
      default:  SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      }
    }
  } else {

    for (int x = 0; x < length; x++) {
      char ch = dataPtr[x];
      switch (ch)
      {
      case '0': SendData(COLOR_BLACK << 4 | COLOR_BLACK); SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      case '1': SendData(COLOR_BLACK << 4 | COLOR_BLACK); SendData(COLOR_BLACK << 4 | COLOR_WHITE); break;
      case '2': SendData(COLOR_BLACK << 4 | COLOR_BLACK); SendData(COLOR_WHITE << 4 | COLOR_BLACK); break;
      case '3': SendData(COLOR_BLACK << 4 | COLOR_BLACK); SendData(COLOR_WHITE << 4 | COLOR_WHITE); break;
      case '4': SendData(COLOR_BLACK << 4 | COLOR_WHITE); SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      case '5': SendData(COLOR_BLACK << 4 | COLOR_WHITE); SendData(COLOR_BLACK << 4 | COLOR_WHITE); break;
      case '6': SendData(COLOR_BLACK << 4 | COLOR_WHITE); SendData(COLOR_WHITE << 4 | COLOR_BLACK); break;
      case '7': SendData(COLOR_BLACK << 4 | COLOR_WHITE); SendData(COLOR_WHITE << 4 | COLOR_WHITE); break;
      case '8': SendData(COLOR_WHITE << 4 | COLOR_BLACK); SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      case '9': SendData(COLOR_WHITE << 4 | COLOR_BLACK); SendData(COLOR_BLACK << 4 | COLOR_WHITE); break;
      case 'a': SendData(COLOR_WHITE << 4 | COLOR_BLACK); SendData(COLOR_WHITE << 4 | COLOR_BLACK); break;
      case 'b': SendData(COLOR_WHITE << 4 | COLOR_BLACK); SendData(COLOR_WHITE << 4 | COLOR_WHITE); break;
      case 'c': SendData(COLOR_WHITE << 4 | COLOR_WHITE); SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      case 'd': SendData(COLOR_WHITE << 4 | COLOR_WHITE); SendData(COLOR_BLACK << 4 | COLOR_WHITE); break;
      case 'e': SendData(COLOR_WHITE << 4 | COLOR_WHITE); SendData(COLOR_WHITE << 4 | COLOR_BLACK); break;
      case 'f': SendData(COLOR_WHITE << 4 | COLOR_WHITE); SendData(COLOR_WHITE << 4 | COLOR_WHITE); break;
      default:  SendData(COLOR_BLACK << 4 | COLOR_BLACK); SendData(COLOR_BLACK << 4 | COLOR_BLACK); break;
      // case '0': SendData(0x00); SendData(0x00); break;
      // case '1': SendData(0x00); SendData(0x03); break;
      // case '2': SendData(0x00); SendData(0x30); break;
      // case '3': SendData(0x00); SendData(0x33); break;
      // case '4': SendData(0x03); SendData(0x00); break;
      // case '5': SendData(0x03); SendData(0x03); break;
      // case '6': SendData(0x03); SendData(0x30); break;
      // case '7': SendData(0x03); SendData(0x33); break;
      // case '8': SendData(0x30); SendData(0x00); break;
      // case '9': SendData(0x30); SendData(0x03); break;
      // case 'a': SendData(0x30); SendData(0x30); break;
      // case 'b': SendData(0x30); SendData(0x33); break;
      // case 'c': SendData(0x33); SendData(0x00); break;
      // case 'd': SendData(0x33); SendData(0x03); break;
      // case 'e': SendData(0x33); SendData(0x30); break;
      // case 'f': SendData(0x33); SendData(0x33); break;
      // default:  SendData(0x00); SendData(0x00); break;
      }
    }
  }
}

void Epd::FrameDataFlush(void) {
  int doublePixels = (EPD_WIDTH * EPD_HEIGHT) >> 1;
  for (int p = 0; p < doublePixels; p++) {
    SendData(0x33);
  }
}

void Epd::FrameDataStop(void) {
  SendCommand(0x11);
}

void Epd::FrameDataShow(void) {
  // Refresh display
  SendCommand(0x12);
  delay(100);
  WaitUntilIdle();

  // Sleep
  SendCommand(0x02);  // Power off
  WaitUntilIdle();
  SendCommand(0x07);
  SendData(0xA5);     // Deep sleep
}

void Epd::SendCommand(unsigned char command) {
  digitalWrite(DC_PIN, LOW);
  SpiTransfer(command);
}

void Epd::SendData(unsigned char data) {
  digitalWrite(DC_PIN, HIGH);
  SpiTransfer(data);
}

void Epd::Sleep(void) {
  SendCommand(POWER_OFF);
  WaitUntilIdle();
  SendCommand(DEEP_SLEEP);
  SendData(0xa5);
}
