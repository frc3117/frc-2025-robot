#pragma once

#include "../FRC-CAN-Arduino/frc_CAN.h"

#include "stdint.h"

#define DIGITAL_INPUTS_ADDRESS 64
#define DIGITAL_INPUTS_SIZE 16

#define DIGITAL_INPUTS_FREQUENCY 20

namespace frc
{
    struct DigitalInputInfo
    {
        bool Reversed: 1;
        uint8_t Pin: 7;
    };
    union DigitalInputsList
    {
        DigitalInputInfo Inputs[DIGITAL_INPUTS_SIZE] {};
        uint8_t Buffer[DIGITAL_INPUTS_SIZE];
    };
    union SetDigitalInputMessage
    {
        struct {
            uint8_t Index;
            DigitalInputInfo Info;
        } Message;
        uint8_t Buffer[2];
    };

    typedef union
    {
        uint64_t num;
        uint8_t data[8];
    } DigitalInputsPacket;

    class DigitalInputs
    {
    public:
        void init();
        void loop(frc::CAN* canDevice);

        void setInput(uint8_t id, uint8_t index, bool reversed = false);
        void clearInputs();

        DigitalInputsPacket generatePacket();

    private:
        unsigned long _lastSent = 0;
        DigitalInputsList _inputList;
    };
}