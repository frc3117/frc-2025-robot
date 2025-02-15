#include "WString.h"
#pragma once

#include "FirmwareMessage.h"

#define FIRMWARE_VERSION_MESSAGE_TYPE 0
#define PROGRAM_VERSION_MESSAGE_TYPE 1
#define LOG_MESSAGE_TYPE 2

class FirmwareBase
{
public:
    const String FirmwareVersion = "1.0.0";
    
    String ProgramVersion;
    int Baudrate;

    FirmwareMessage IncomingMessage;
    FirmwareMessage OutgoingMessage;

    FirmwareBase(String programVersion, int baudrate);

    void init();
    void loop();

    void sendFirmwareVersion();
    void sendProgramVersion();

    void sendLog(String* log);

private:
    bool isMessageStarted = false;
    uint8_t bytesLeft = 4;
};