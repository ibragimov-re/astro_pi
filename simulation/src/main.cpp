#include "pch.h"
#include "board_orangepi3lts.h"
#include "ks_binder.h"
#include "utils.h"
#include "gpio_test.h"
#include "iostream"
#include <chrono>


int main() {

    try {
        consoleUtils::printMessage(L"KOPIS (Kompas-3D Orange Pi Simulator)\n\n");
        
        consoleUtils::printMessage(L"Setting up board...\n");
        auto startTimeSetupBoard = std::chrono::high_resolution_clock::now();
        OrangePi3LTS board;
        KsBinder ksBinder(board);
        auto endTimeSetupBoard = std::chrono::high_resolution_clock::now();
        auto durationInMillisecondsSetupBoard = duration_cast<std::chrono::milliseconds>(endTimeSetupBoard - startTimeSetupBoard);

        consoleUtils::printMessage(L"[OK] Board setup done. Duration: " +
            std::to_wstring(durationInMillisecondsSetupBoard.count()) + L" ms\n");
        


        consoleUtils::printMessage(L"\nRunning GPIO program...\n");
        auto startTimeRunGpioProg = std::chrono::high_resolution_clock::now();


        // Запуск тестового кода
        // В будущем здесь будет выполняться код управляющей программы на python через обертку pybind
        gpioTest::RunGpioProgram(board);


        auto endTimeRunGpioProg = std::chrono::high_resolution_clock::now();
        auto durationInMillisecondsRunGpioProg = duration_cast<std::chrono::milliseconds>(endTimeRunGpioProg - startTimeRunGpioProg);

        consoleUtils::printMessage(L"[OK] GPIO program finished. Duration: " +
            std::to_wstring(durationInMillisecondsRunGpioProg.count()) + L" ms\n\n");



        consoleUtils::printMessage(L"Turning simulator off...\n");
    }
    catch (const std::exception& ex) {
        std::cerr << "# [PROGRAM CRASHED] " << "Exception: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}