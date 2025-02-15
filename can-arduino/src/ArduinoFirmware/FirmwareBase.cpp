#include "WString.h"
#include "HardwareSerial.h"
#include "FirmwareBase.h"

FirmwareBase::FirmwareBase(String programVersion, int baudrate)
{
  ProgramVersion = programVersion;
  Baudrate = baudrate;
}

void FirmwareBase::init()
{
    Serial.begin(Baudrate);
}
void FirmwareBase::loop()
{
    if (Serial.available() >= bytesLeft)
    {

    }
}

void FirmwareBase::sendFirmwareVersion()
{
    OutgoingMessage.reset().setMessageType(FIRMWARE_VERSION_MESSAGE_TYPE).addString(&FirmwareVersion).sendMessage().reset();
}
void FirmwareBase::sendProgramVersion()
{
    OutgoingMessage.reset().setMessageType(PROGRAM_VERSION_MESSAGE_TYPE).addString(&ProgramVersion).sendMessage().reset();
}

void FirmwareBase::sendLog(String* log)
{
    OutgoingMessage.reset().setMessageType(LOG_MESSAGE_TYPE).addString(log).sendMessage().reset();
}