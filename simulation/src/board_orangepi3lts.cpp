#include <stdexcept>
#include <iostream>
#include <iomanip>
#include <functional>
#include "board_orangepi3lts.h"


// Определение конструктора платы
OrangePi3LTS::OrangePi3LTS() {
    // Добавление умных указателей на пины в общий контейнер
    pins.emplace_back(std::make_unique<PowerPin>   (1,  "3.3V"                             ));
    pins.emplace_back(std::make_unique<PowerPin>   (2,  "5V"                               ));
    pins.emplace_back(std::make_unique<SpecialPin> (3,  "SDA.0",  "PD26", 122, "TWI0-SDA"  ));
    pins.emplace_back(std::make_unique<PowerPin>   (4,  "5V"                               ));
    pins.emplace_back(std::make_unique<SpecialPin> (5,  "SCL.0",  "PD25", 121, "TWI0-SCK"  ));
    pins.emplace_back(std::make_unique<GroundPin>  (6,  "GND"                              ));
    pins.emplace_back(std::make_unique<SpecialPin> (7,  "PWM.0",  "PD22", 118, "PWM0"      ));
    pins.emplace_back(std::make_unique<GpioPin>    (8,  "PL02",   "PL2",  354              ));
    pins.emplace_back(std::make_unique<GroundPin>  (9,  "GND"                              ));
    pins.emplace_back(std::make_unique<GpioPin>    (10, "PL03",   "PL3",  355              ));
    pins.emplace_back(std::make_unique<SpecialPin> (11, "RXD.3",  "PD24", 120, "UART3_RX"  ));
    pins.emplace_back(std::make_unique<GpioPin>    (12, "PD18",   "PD18", 114              ));
    pins.emplace_back(std::make_unique<SpecialPin> (13, "TXD.3",  "PD23", 119, "UART3_TX"  ));
    pins.emplace_back(std::make_unique<GroundPin>  (14, "GND"                              ));
    pins.emplace_back(std::make_unique<GpioPin>    (15, "PL10",   "PL10", 362              ));
    pins.emplace_back(std::make_unique<GpioPin>    (16, "PD15",   "PD15", 111              ));
    pins.emplace_back(std::make_unique<PowerPin>   (17, "3.3V"                             ));
    pins.emplace_back(std::make_unique<GpioPin>    (18, "PD16",   "PD16", 112              ));
    pins.emplace_back(std::make_unique<SpecialPin> (19, "MOSI.1", "PH5",  229, "SPI1_MOSI" ));
    pins.emplace_back(std::make_unique<GroundPin>  (20, "GND"                              ));
    pins.emplace_back(std::make_unique<SpecialPin> (21, "MISO.1", "PH6",  230, "SPI1_MISO" ));
    pins.emplace_back(std::make_unique<GpioPin>    (22, "PD21",   "PD21", 117              ));
    pins.emplace_back(std::make_unique<SpecialPin> (23, "SCLK.1", "PH4",  228, "SPI1_SCLK" ));
    pins.emplace_back(std::make_unique<SpecialPin> (24, "CE.1",   "PH3",  227, "SPI1_CS"   ));
    pins.emplace_back(std::make_unique<GroundPin>  (25, "GND"                              ));
    pins.emplace_back(std::make_unique<GpioPin>    (26, "PL08",   "PL8",  360              ));
}


Pin& OrangePi3LTS::getPinByBoardNumber(int boardNumber) const {
    for (const auto& pin : pins) {
        if (pin->getBoardNumber() == boardNumber) {
            return *pin;
        }
    }
    throw std::out_of_range("No pin with this board number");
}


Pin& OrangePi3LTS::getPinBySocName(const std::string& socName) const {
    for (const auto& pin : pins) {
        const auto pinType = pin->getType();
        if (pinType != PinType::GPIO && pinType != PinType::SPECIAL) {
            continue;
        }

        GpioPin& gpioPin = static_cast<GpioPin&>(*pin);
        if (gpioPin.getSocName() == socName) {
            return *pin;
        }
    }
    throw std::out_of_range("No pin with this SoC name");
}


std::vector<std::reference_wrapper<Pin>> OrangePi3LTS::getAllPins() const {
    std::vector<std::reference_wrapper<Pin>> result; // Обертка reference_wrapper для хранения ссылок на пины в контейнере
    for (const auto& pin : pins) {
        result.push_back(*pin); // Разыменовать указатель и добавить ссылку на пин в вектор
    }
    return result;
}


void OrangePi3LTS::printBoardPins() const {
    std::cout << "+------+-------+----------+------+---+  #KOPIS  +---+------+----------+-------+------+\n";
    std::cout << "| GPIO |  SoC  |   Name   | Mode | V | ~Virtual | V | Mode |   Name   |  SoC  | GPIO |\n";
    std::cout << "+------+-------+----------+------+---+----++----+---+------+----------+-------+------+\n";

    auto allPins = getAllPins();
    for (size_t i = 0; i < allPins.size(); i += 2) {
        Pin& leftPin = allPins[i];
        Pin& rightPin = allPins[i + 1];


        // Лямбла-выражение. Принимает ссылку на пин и возвращает контейнер со значениями пина
        auto formatPin = [](Pin& pin) {
            std::string gpioNum = "";
            std::string soc = "";
            std::string name = pin.getName();
            std::string mode = "";
            std::string val = "";

            if (pin.getType() == PinType::GPIO) {
                GpioPin& gPin = static_cast<GpioPin&>(pin);
                gpioNum = std::to_string(gPin.getGpioNumber());
                switch (gPin.getMode()) {
                    case GpioMode::OFF:    mode = "OFF"; break;
                    case GpioMode::INPUT:  mode = "IN";  break;
                    case GpioMode::OUTPUT: mode = "OUT"; break;
                    default: mode = ""; break;
                }
                val = (gPin.getState() == GpioState::HIGH ? "1" : "0");
                soc = (gPin.getSocName());
            }
            else if (pin.getType() == PinType::SPECIAL) {
                SpecialPin& sPin = static_cast<SpecialPin&>(pin);
                gpioNum = std::to_string(sPin.getGpioNumber());
                switch (sPin.getMode()) {
                    case GpioMode::OFF:    mode = "OFF"; break;
                    case GpioMode::INPUT:  mode = "IN";  break;
                    case GpioMode::OUTPUT: mode = "OUT"; break;
                    case GpioMode::ALT:    mode = "ALT"; break;
                    default: mode = ""; break;
                }
                val = (sPin.getMode() == GpioMode::ALT ? "-" : (sPin.getState() == GpioState::HIGH ? "1" : "0"));
                soc = (sPin.getSocName());
            }

            return std::tuple{ gpioNum, soc, name, mode, val };
        };

        auto [lGpio, lSoc, lName, lMode, lVal] = formatPin(leftPin);
        auto [rGpio, rSoc, rName, rMode, rVal] = formatPin(rightPin);

        std::cout << "| " << std::setw(4) << std::right << lGpio
            << " | " << std::setw(5) << std::right << lSoc
            << " | " << std::setw(8) << std::right << lName
            << " | " << std::setw(4) << std::right << lMode
            << " | " << std::setw(1) << std::right << lVal
            << " | " << std::setw(2) << i + 1
            << " || "<< std::setw(2) << std::left << i + 2
            << " | " << std::setw(1) << std::left << rVal
            << " | " << std::setw(4) << std::left << rMode
            << " | " << std::setw(8) << std::left << rName
            << " | " << std::setw(5) << std::left << rSoc
            << " | " << std::setw(4) << std::left << rGpio
            << " |\n";
    }

    std::cout << "+------+-------+----------+------+---+----++----+---+------+----------+-------+------+\n";
    std::cout << "| GPIO |  SoC  |   Name   | Mode | V | ~Virtual | V | Mode |   Name   |  SoC  | GPIO |\n";
    std::cout << "+------+-------+----------+------+---+  #KOPIS  +---+------+----------+-------+------+\n";
}