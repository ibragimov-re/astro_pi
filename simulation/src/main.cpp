#include <pybind11/pybind11.h>
#include <chrono>
#include <stdexcept>
#include "pch.h"
#include "board_orangepi3lts.h"
#include "ks_binder.h"
#include "utils.h"
#include "gpio_test.h"
#include "iostream"
#include "pin.h"

namespace py = pybind11;
//TO DO: комментарии к функциям

// режим нумерации пинов
enum class PinNumberingMode {
	NONE, // по умолчанию
	BOARD,
	BCM,
	SUNXI
};


static std::unique_ptr<OrangePi3LTS> g_board;
static std::unique_ptr<KsBinder> g_binder;
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
		// инициализация объектов при загрузке модуля
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

		// очистка указателей на объекты при выгрузке модуля
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

	py::enum_<GpioState>(m, "GpioState")
		.value("LOW", GpioState::LOW)
		.value("HIGH", GpioState::HIGH)
		.export_values();

	py::enum_<PinType>(m, "PinType")
		.value("GPIO", PinType::GPIO)
		.value("SPECIAL", PinType::SPECIAL)
		.value("POWER", PinType::POWER)
		.value("GROUND", PinType::GROUND)
		.export_values();

	py::enum_<GpioMode>(m, "GpioMode")
		.value("IN", GpioMode::INPUT)
		.value("OUT", GpioMode::OUTPUT)
		.export_values();


	m.def("setmode", [](PinNumberingMode mode) {
		g_numberingMode = mode;
	}, "set pin numbering mode" );
	

	m.def("getmode", []() -> PinNumberingMode {
		return g_numberingMode;
	}, "get pin numbering mode");


	m.def("setup", [](const int pinNumber, const GpioMode mode) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw (std::runtime_error("GPIO numbering mode is not set"));
		}
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setMode(mode);
	}, "set selected pin (by number) to INPUT or OUTPUT mode");
	

	m.def("setup", [](const std::string& socName, const GpioMode mode) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		gpioPin.setMode(mode);
	}, "set selected pin (by socket name) to INPUT or OUTPUT mode");


	m.def("output", [](const int pinNumber, const GpioState state) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setState(state);
	}, "set selected pin's value (by number) as HIGH or LOW");
	

	m.def("output", [](const std::string& socName, const GpioState state) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		gpioPin.setState(state);
	}, "set selected pin's value (by socket name) as HIGH or LOW");
		

	m.def("setwarnings", [](bool isWarningsSet) {
		if (isWarningsSet) {
			throw std::runtime_error("This feature is not supported now");
		}
	},"enable or disable warnings");


	m.def("cleanup", [] {
		auto pinsVec = g_board->getAllPins();
		
		for (auto& pinRef : pinsVec) {
			Pin& pin = pinRef.get();
			if (pin.getType() == PinType::GPIO || pin.getType() == PinType::SPECIAL) {
				auto& gpioPin = static_cast<GpioPin&>(pin);
				gpioPin.setMode(GpioMode::INPUT);
			};
		}
	}, "set all GPIO and special pins to the default mode");


	m.def("cleanup", [](const int pinNumber) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw (std::runtime_error("GPIO numbering mode is not set"));
		}
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setMode(GpioMode::INPUT);
	}, "set selected pin (by number) to the default mode");


	m.def("cleanup", [](const std::string& socName) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}
		GpioPin& pin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		pin.setMode(GpioMode::INPUT);
	}, "set selected pin (by socket name) to the default mode");
}