#include <pybind11/pybind11.h>
#include <chrono>
#include <stdexcept>
#include "pch.h"
#include "board_orangepi3lts.h"
#include "ks_binder.h"
#include "utils.h"
#include "gpio_test.h"
#include "iostream"


namespace py = pybind11;

static std::unique_ptr<OrangePi3LTS> g_board;
static std::unique_ptr<KsBinder> g_binder;

// Режимм нумерации пинов
enum class PinNumberingMode {
    NONE, // по умолчанию
    BOARD,
    BCM,
    SUNXI
};

// Режим GPIO пина
enum class GpioMode {
    OFF, // по умолчанию
    INPUT,
    OUTPUT
};

// TO DO: Добавить PinState сюда и в pybind module


static PinNumberingMode g_numberingMode = PinNumberingMode::NONE;

void init_board() {
    consoleUtils::printMessage(L"KOPIS (Kompas-3D Orange Pi Simulator)\n\n");

    consoleUtils::printMessage(L"Setting up board...\n");

    auto startTimeSetupBoard = std::chrono::high_resolution_clock::now();
    g_board = std::make_unique<OrangePi3LTS>();
    g_binder = std::make_unique<KsBinder>(*g_board);
    auto endTimeSetupBoard = std::chrono::high_resolution_clock::now();

    auto durationInMillisecondsSetupBoard = duration_cast<std::chrono::milliseconds>(endTimeSetupBoard - startTimeSetupBoard);
    consoleUtils::printMessage(L"[OK] Board setup done. Duration: " +
        std::to_wstring(durationInMillisecondsSetupBoard.count()) + L" ms\n");
}

// Capsule класс для управления временем жизни
struct BoardCapsule {
    std::chrono::high_resolution_clock::time_point startTimeRunGpioProg;

    BoardCapsule() {
        // Инициализация объектов при загрузке модуля
        init_board();

        consoleUtils::printMessage(L"\nRunning GPIO program...\n");
        startTimeRunGpioProg = std::chrono::high_resolution_clock::now();
    }
    ~BoardCapsule() {
        auto endTimeRunGpioProg = std::chrono::high_resolution_clock::now();
        auto durationInMillisecondsRunGpioProg = duration_cast<std::chrono::milliseconds>(endTimeRunGpioProg - startTimeRunGpioProg);
        consoleUtils::printMessage(L"[OK] GPIO program finished. Duration: " +
            std::to_wstring(durationInMillisecondsRunGpioProg.count()) + L" ms\n\n");

        consoleUtils::printMessage(L"Turning simulator off...\n");

        // Очистка указателей на объекты при выгрузке модуля
        g_binder.reset();
        g_board.reset();
    }
};


PYBIND11_MODULE(kopis, m) {
    m.doc() = "KOPIS (Kompas-3D Orange Pi Simulator) Python module";

    // создание capsule и привязка к модулю
    py::capsule capsule = py::capsule(new BoardCapsule(), [](void* ptr) {
        delete static_cast<BoardCapsule*>(ptr);
    });
    m.add_object("_board_capsule", capsule);

    py::enum_<PinNumberingMode>(m, "PinNumberingMode")
        .value("BOARD", PinNumberingMode::BOARD)
        .value("BCM", PinNumberingMode::BCM)
        .value("SUNXI", PinNumberingMode::SUNXI)
        .export_values();

    py::enum_<GpioMode>(m, "GpioMode")
        .value("IN", GpioMode::INPUT)
        .value("OUT", GpioMode::OUTPUT)
        .export_values();

    m.def("setmode", [](PinNumberingMode mode) {
        g_numberingMode = mode;
    });

    m.def("getmode", []() -> PinNumberingMode {
        return g_numberingMode;
    });

    m.def("setup", [](int pinNumber, PinMode mode) {
        if (g_numberingMode == PinNumberingMode::NONE) {
            throw std::runtime_error("GPIO numbering mode is not set");
        }

        GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
        
        // TO DO: Дописать логику метода и добавить перегрузку для типа string (для нахождения по SUNXI)
    });

    m.def("output", [](int pinNumber) {
        GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
        
        // TO DO: Дописать логику метода и добавить перегрузку для типа string (для нахождения по SUNXI)
    });

    // TO DO: Дописать другие методы для макетной библиотеки
}