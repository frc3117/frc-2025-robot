#include "WString.h"
#pragma once

#define MESSAGE_SIZE 256

class FirmwareMessage
{
public:
    FirmwareMessage();

    FirmwareMessage reset();

    FirmwareMessage setMessageType(uint8_t messageType);
    uint8_t getMessageType();

    uint8_t getMessageLength();

    FirmwareMessage addBytes(void* value, uint8_t length);
    FirmwareMessage addBytes(const void *value, uint8_t length);
    void* getBytes(void* value, unsigned char length);

    FirmwareMessage addUnsignedChar(unsigned char value);
    unsigned char getUnsignedChar();

    FirmwareMessage addChar(char value);
    char getChar();

    FirmwareMessage addShort(short value);
    short getShort();

    FirmwareMessage addInt(int value);
    int getInt();

    FirmwareMessage addString(String* value);
    FirmwareMessage addString(const String* value);
    String getString();

    FirmwareMessage sendMessage();

private:
    FirmwareMessage updateMessageLength();

    uint8_t bufferPosition = 0;
    uint8_t messageBuffer[MESSAGE_SIZE]{};
};

/*
  $$: Start of message
  uint8: MessageLength
  uint8: MessageType

  byte[sizeof(type)] : Param1
  byte[sizeof(type)] : Param2
  ...
*/