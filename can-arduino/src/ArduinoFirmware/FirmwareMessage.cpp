#include "Arduino.h"
#include "WString.h"
#include "FirmwareMessage.h"
#include "HardwareSerial.h"

#include <string.h>

FirmwareMessage::FirmwareMessage()
{
    messageBuffer[0] = '$';
    messageBuffer[1] = '$';

    setMessageType(0).reset();
}

FirmwareMessage FirmwareMessage::reset()
{
    bufferPosition = 4;

    return updateMessageLength();
}

FirmwareMessage FirmwareMessage::setMessageType(uint8_t messageType)
{
    memcpy(messageBuffer + 3, &messageType, sizeof(uint8_t));

    return *this;
}
unsigned char FirmwareMessage::getMessageType()
{
    unsigned char value = 0;

    memcpy(&value, messageBuffer + 3, sizeof(uint8_t));

    return value;
}

uint8_t FirmwareMessage::getMessageLength()
{
    uint8_t value = 0;

    memcpy(&value, messageBuffer + 2, sizeof(uint8_t));

    return value;
}

FirmwareMessage FirmwareMessage::addBytes(void* value, uint8_t length)
{
    memcpy(messageBuffer + bufferPosition, value, length);
    bufferPosition += length;

    return updateMessageLength();
}
FirmwareMessage FirmwareMessage::addBytes(const void *value, uint8_t length)
{
    memcpy(messageBuffer + bufferPosition, value, length);
    bufferPosition += length;

    return updateMessageLength();
}
void* FirmwareMessage::getBytes(void *value, unsigned char length)
{
    memcpy(value, messageBuffer + bufferPosition, length);
    bufferPosition += length;

    return value;
}

FirmwareMessage FirmwareMessage::addUnsignedChar(unsigned char value)
{
    return addBytes(&value, sizeof(unsigned char));
}
unsigned char FirmwareMessage::getUnsignedChar()
{
    unsigned char value = 0;
    getBytes(&value, sizeof(unsigned char));

    return value;
}

FirmwareMessage FirmwareMessage::addChar(char value)
{
    return addBytes(&value, sizeof(char));
}
 char FirmwareMessage::getChar()
{
    char value = 0;
    getBytes(&value, sizeof(char));

    return value;
}

FirmwareMessage FirmwareMessage::addShort(short value)
{
    return addBytes(&value, sizeof(short));
}
short FirmwareMessage::getShort()
{
    short value = 0;
    getBytes(&value, sizeof(short));

    return value;
}

FirmwareMessage FirmwareMessage::addInt(int value)
{
    return addBytes(&value, sizeof(int));
}
int FirmwareMessage::getInt()
{
    int value = 0;
    getBytes(&value, sizeof(int));

    return value;
}

FirmwareMessage FirmwareMessage::addString(String* value)
{
    unsigned char length = value->length();
    return addUnsignedChar(length).addBytes(value->c_str(), length);
}
FirmwareMessage FirmwareMessage::addString(const String *value)
{
    unsigned char length = value->length();
    return addUnsignedChar(length).addBytes(value->c_str(), length);
}
String FirmwareMessage::getString()
{
    unsigned char length = getUnsignedChar();

    char* value = new char[length + 1];
    getBytes(value, length);

    value[length] = '\0';
    return {value};
}

FirmwareMessage FirmwareMessage::sendMessage()
{
    Serial.write(messageBuffer, getMessageLength() + 3);

    return *this;
}

FirmwareMessage FirmwareMessage::updateMessageLength()
{
    bufferPosition -= 3;
    memcpy(messageBuffer + 2, &bufferPosition, sizeof(uint8_t));
    bufferPosition += 3;

    return *this;
}