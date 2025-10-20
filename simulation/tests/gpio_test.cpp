#include "gpio_test.h"
#include "utils.h"
#include <Windows.h> // Для Sleep
#include <chrono>


namespace gpioTest {
    
    void RunGpioProgram(OrangePi3LTS& board) {
        consoleUtils::printMessage(L"[TEST] Запущена тестовая управляющая программа\n");


        consoleUtils::printMessage(L"[TEST] Установка OUTPUT режима у GPIO пинов\n");
        GpioPin& pin12 = static_cast<GpioPin&>(board.getPinByBoardNumber(12));
        pin12.setMode(PinMode::OUTPUT);
        GpioPin& pin15 = static_cast<GpioPin&>(board.getPinBySocName("PL10"));
        pin15.setMode(PinMode::OUTPUT);


        consoleUtils::printMessage(L"[TEST] Замер скорости переключения состояния GPIO пина:\n");
        for (int i = 0; i < 15; ++i) {
            auto startTime = std::chrono::high_resolution_clock::now();
            pin12.setState(GpioState::HIGH);
            auto endTime = std::chrono::high_resolution_clock::now();
            auto durationInMilliseconds = duration_cast<std::chrono::milliseconds>(endTime - startTime);

            consoleUtils::printMessage(L"-> " + std::to_wstring(durationInMilliseconds.count()) + L" ms\n");

            pin12.setState(GpioState::LOW);
        }


        consoleUtils::printMessage(L"[TEST] Установка INPUT режима у GPIO пина\n");
        GpioPin& pin11 = static_cast<GpioPin&>(board.getPinByBoardNumber(11));
        pin11.setMode(PinMode::INPUT);


        consoleUtils::printMessage(L"[TEST] Установка ALT режима у SPECIAL пинов\n");
        GpioPin& pin19 = static_cast<SpecialPin&>(board.getPinByBoardNumber(19));
        pin19.setMode(PinMode::ALT);
        GpioPin& pin21 = static_cast<SpecialPin&>(board.getPinByBoardNumber(21));
        pin21.setMode(PinMode::ALT);
        GpioPin& pin23 = static_cast<SpecialPin&>(board.getPinByBoardNumber(23));
        pin23.setMode(PinMode::ALT);


        consoleUtils::printMessage(L"[TEST] Переключение состояния GPIO пинов с разной скоростью\n");
        for (int i = 200; i >= 0; i -= 10) {
            pin12.setState(GpioState::HIGH);
            Sleep(i);
            pin12.setState(GpioState::LOW);
            Sleep(i);
            pin15.setState(GpioState::HIGH);
            Sleep(i);
            pin15.setState(GpioState::LOW);
            Sleep(i);
            pin15.setState(GpioState::HIGH);
            Sleep(i);
            pin15.setState(GpioState::LOW);
            Sleep(i);
        }


        consoleUtils::printMessage(L"[TEST] Выключение GPIO пинов\n");
        pin12.setMode(PinMode::OFF);
        pin15.setMode(PinMode::OFF);
        pin11.setMode(PinMode::OFF);


        consoleUtils::printMessage(L"[TEST] Переключение SPECIAL пинов в OUTPUT режим\n");
        pin19.setMode(PinMode::OUTPUT);
        pin21.setMode(PinMode::OUTPUT);
        pin23.setMode(PinMode::OUTPUT);


        consoleUtils::printMessage(L"[TEST] Переключение состояния SPECIAL пинов с максимальной скоростью\n");
        for (int i = 0; i < 20; ++i) {
            pin19.setState(GpioState::HIGH);
            pin19.setState(GpioState::LOW);
            pin21.setState(GpioState::HIGH);
            pin21.setState(GpioState::LOW);
            pin23.setState(GpioState::HIGH);
            pin23.setState(GpioState::LOW);
        }


        consoleUtils::printMessage(L"[TEST] Выключение SPECIAL пинов\n");
        pin19.setMode(PinMode::OFF);
        pin21.setMode(PinMode::OFF);
        pin23.setMode(PinMode::OFF);


        consoleUtils::printMessage(L"[TEST] Тестовая управляющая программа завершена\n");
    }
}