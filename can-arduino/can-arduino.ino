#include "./src/FRC-CAN-Arduino/frc_mcp2515.h"
#include "./src/FRC-CAN-Arduino/frc_CAN.h"
#include "./src/ArduinoFirmware/DigitalInputs.h"

#define CAN_CS 4
#define CAN_INTERRUPT 2

frc::MCP2515 mcp2515{CAN_CS};
frc::CAN frcCANDevice{1};

frc::DigitalInputs digitalInputs{};

void CANCallback(frc::CAN* can, int apiId, bool rtr, const frc::CANData& data)
{

}

/*void CANCallback(frc::CAN* can, int apiId, bool rtr, const frc::CANData& data)
{
    switch (apiId)
    {
        case 0: // Set digital input
            frc::SetDigitalInputMessage message{};
            memcpy(message.Buffer, data.data, 2);

            digitalInputs.setInput(message.Message.Info.Pin, message.Message.Index, message.Message.Info.Reversed);
            break;
    }

    Serial.println(apiId);
}*/

void setup()
{
    auto err = mcp2515.reset();
    err = mcp2515.setBitrate(frc::CAN_1000KBPS, frc::CAN_CLOCK::MCP_16MHZ);
    err = mcp2515.setNormalMode();

    pinMode(CAN_INTERRUPT, INPUT);

    frc::CAN::SetCANImpl(&mcp2515, CAN_INTERRUPT, CANCallback, nullptr);
    frcCANDevice.AddToReadList();

    digitalInputs.init();

    Serial.begin(9600);

    digitalInputs.setInput(3, 0, true);
}

void loop()
{
    frc::CAN::Update();
    digitalInputs.loop(&frcCANDevice);
}