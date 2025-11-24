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
#include "assembly.h"


namespace py = pybind11;


// тип монтировки
enum class MountType {
	EQ, // По умолчанию
	AZ
};


// режим нумерации пинов
enum class PinNumberingMode {
	NONE, // по умолчанию
	BOARD,
	SUNXI
};


// Умный указатель на Assembly — владеет объектом и управляет временем жизни
static std::unique_ptr<Assembly> g_assembly;

// Обычный указатель на объект платы внутри Assembly.
// Объект управляется g_assembly, поэтому g_board не владеет памятью
static const OrangePi3LTS* g_board;

// Умный указатель на KsBinder — владеет объектом
static std::unique_ptr<KsBinder> g_binder;

// По умолчанию тип монтировки - экваториальная
static MountType g_mountType = MountType::EQ;

static PinNumberingMode g_numberingMode = PinNumberingMode::NONE;


// Выставление моторов в исходное положение для экваториальной монтировки
void setupMotorsForEQMount() {
	Motor& motorHorizontal = g_assembly->getMotor(L"#Nema17HS8401_Horizontal");
	Motor& motorVertical = g_assembly->getMotor(L"#Nema17HS8401_Vertical");
	motorHorizontal.setShaftAngle(0);
	motorVertical.setShaftAngle(90);
}


// Выставление моторов в исходное положение для азимутальной монтировки
void setupMotorsForAZMount() {
	Motor& motorHorizontal = g_assembly->getMotor(L"#Nema17HS8401_Horizontal");
	Motor& motorVertical = g_assembly->getMotor(L"#Nema17HS8401_Vertical");
	motorHorizontal.setShaftAngle(0);
	motorVertical.setShaftAngle(0);
}


// Выставление моторов в исходное положение в зависимости от типа монтировки
void setupMotors() {
	if (g_mountType == MountType::EQ) setupMotorsForEQMount();
	else setupMotorsForAZMount();
}


void initBoard() {
	consoleUtils::printMessage(L"\n============================================\n");
	consoleUtils::printMessage(L"KOPIS (Kompas-3D Orange Pi Simulator) v" + strUtils::strToWStr(KOPIS_VERSION));
	consoleUtils::printMessage(L"\n============================================\n");

	consoleUtils::printMessage(L"[KOPIS] Setting up board...\n");

	auto startTimeSetupBoard = std::chrono::high_resolution_clock::now();
	g_assembly = std::make_unique<Assembly>();

	// Взять адрес объекта платы внутри Assembly и присвоить указателю
	// g_board не будет владеть объектом, просто указывает на существующий объект
	g_board = &g_assembly->getBoard();

	g_binder = std::make_unique<KsBinder>(*g_assembly);
	auto endTimeSetupBoard = std::chrono::high_resolution_clock::now();

	setupMotors();

	auto durationInMillisecondsSetupBoard = duration_cast<std::chrono::milliseconds>(endTimeSetupBoard - startTimeSetupBoard);
	consoleUtils::printMessage(L"[KOPIS] [OK] Board setup done. Duration: " +
		std::to_wstring(durationInMillisecondsSetupBoard.count()) + L" ms\n");
}


// Проверка требуемого режима нумерации пинов
void checkRequiredNumberingMode(PinNumberingMode reqNumberingMode) {
	if (g_numberingMode == reqNumberingMode) {
		return;
	}

	if (g_numberingMode == PinNumberingMode::NONE) {
		throw std::runtime_error("GPIO numbering mode is not set. Use ""GPIO.setmode()"" first");
	}

	if ((g_numberingMode != reqNumberingMode) && (reqNumberingMode == PinNumberingMode::BOARD)) {
		throw (std::runtime_error("GPIO numbering mode by BOARD is not set. Use ""GPIO.setmode(GPIO.BOARD)"" first"));
	}

	if ((g_numberingMode != reqNumberingMode) && (reqNumberingMode == PinNumberingMode::SUNXI)) {
		throw (std::runtime_error("GPIO numbering mode by SUNXI is not set. Use ""GPIO.setmode(GPIO.SUNXI)"" first"));
	}

	throw (std::runtime_error("Unknown GPIO numbering mode"));
}


// Capsule класс для управления временем жизни
struct BoardCapsule {
	std::chrono::high_resolution_clock::time_point startTimeRunGpioProg;

	BoardCapsule() {
		// инициализация объектов при загрузке модуля
		initBoard();

		consoleUtils::printMessage(L"\n[KOPIS] Running GPIO program...\n");
		startTimeRunGpioProg = std::chrono::high_resolution_clock::now();
	}
	~BoardCapsule() {
		// Возвращение моторов в исходное положение
		setupMotors();

		auto endTimeRunGpioProg = std::chrono::high_resolution_clock::now();
		auto durationInMillisecondsRunGpioProg = duration_cast<std::chrono::milliseconds>(endTimeRunGpioProg - startTimeRunGpioProg);
		consoleUtils::printMessage(L"[KOPIS] GPIO program finished. Duration: " +
			std::to_wstring(durationInMillisecondsRunGpioProg.count()) + L" ms\n\n");

		consoleUtils::printMessage(L"[KOPIS] Turning simulator off...\n");

		// очистка указателей на объекты при выгрузке модуля
		g_binder.reset();
		g_assembly.reset();
	}
};



PYBIND11_MODULE(kopis, m) {
	m.doc() = "KOPIS (Kompas-3D Orange Pi Simulator) Python module";

	// Версия модуля из CMake
	m.attr("__version__") = KOPIS_VERSION;

	// создание capsule и привязка к модулю
	py::capsule capsule = py::capsule(new BoardCapsule(), [](void* ptr) {
		delete static_cast<BoardCapsule*>(ptr);
		});
	m.add_object("_board_capsule", capsule);

	py::enum_<PinNumberingMode>(m, "PinNumberingMode")
		.value("BOARD", PinNumberingMode::BOARD)
		.value("BCM", PinNumberingMode::BOARD) // BCM - аналог BOARD
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
		checkRequiredNumberingMode(PinNumberingMode::BOARD);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setMode(mode);
	}, "set selected pin (by number) to INPUT or OUTPUT mode");
	

	m.def("setup", [](const std::string& socName, const GpioMode mode) {
		checkRequiredNumberingMode(PinNumberingMode::SUNXI);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		gpioPin.setMode(mode);
	}, "set selected pin (by socket name) to INPUT or OUTPUT mode");


	m.def("output", [](const int pinNumber, const GpioState state) {
		checkRequiredNumberingMode(PinNumberingMode::BOARD);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setState(state);
	}, "set selected pin's value (by number) as HIGH or LOW");


	m.def("output", [](const int pinNumber, int value) {
		checkRequiredNumberingMode(PinNumberingMode::BOARD);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		GpioState state = (value == 0) ? GpioState::LOW : GpioState::HIGH;
		gpioPin.setState(state);
	}, "set selected pin's value (by number) as 1 or 0");
	

	m.def("output", [](const std::string& socName, const GpioState state) {
		checkRequiredNumberingMode(PinNumberingMode::SUNXI);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		gpioPin.setState(state);
	}, "set selected pin's value (by socket name) as HIGH or LOW");
	

	m.def("output", [](const std::string& socName, int value) {
		checkRequiredNumberingMode(PinNumberingMode::SUNXI);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		GpioState state = (value == 0) ? GpioState::LOW : GpioState::HIGH;
		gpioPin.setState(state);
	}, "set selected pin's value (by socket name) as 1 or 0");


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
		checkRequiredNumberingMode(PinNumberingMode::BOARD);
		GpioPin& gpioPin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
		gpioPin.setMode(GpioMode::INPUT);
	}, "set selected pin (by number) to the default mode");


	m.def("cleanup", [](const std::string& socName) {
		checkRequiredNumberingMode(PinNumberingMode::SUNXI);
		GpioPin& pin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
		pin.setMode(GpioMode::INPUT);
	}, "set selected pin (by socket name) to the default mode");



	// Подмодуль для управления моторами в симуляторе
	py::module_ kopis_motorsim = m.def_submodule("kopis_motorsim", "Motor control submodule for simulator");

	py::enum_<MountType>(kopis_motorsim, "MountType")
		.value("EQ", MountType::EQ)
		.value("AZ", MountType::AZ)
		.export_values();

	kopis_motorsim.def("setup_motors_by_mount_type", [](MountType type) {
		g_mountType = type;
		if (type == MountType::EQ) {
			setupMotorsForEQMount();
		}
		else {
			setupMotorsForAZMount();
		}
	}, "setup motors by mount type");


	kopis_motorsim.def("move_degrees", [](const std::string& motorName, const double angle, const int speed) {
		// Принимаем string из-за ограничений Python и конвертируем в wstring
		Motor& motor = g_assembly->getMotor(strUtils::strToWStr(motorName));
		motor.rotateShaftAngle(angle, speed);
	}, "rotate motor by name, angle and speed");


	kopis_motorsim.def("reset_angle", [](const std::string& motorName) {
		Motor& motor = g_assembly->getMotor(strUtils::strToWStr(motorName));
		motor.resetShaftAngle();
		}, "reset motor angle by name");



	// Подмодуль для дополнительных функций
	py::module_ kopis_extra = m.def_submodule("kopis_extra", "Submodule for additional functionality");

	kopis_extra.def("test_gpio_pins", []() {
		tests::RunGpioPinsTest(*g_assembly);
		}, "runs test program for GPIO pins");


	kopis_extra.def("test_motors", []() {
		tests::RunMotorsTest(*g_assembly);
		}, "runs test program for motors");


	kopis_extra.def("print_board_pins", []() {
		g_board->printBoardPins();
		}, "prints table with all pins information");
}