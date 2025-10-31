#include <pybind11/pybind11.h>
#include <chrono>
#include <stdexcept>
#include "pch.h"
#include "board_orangepi3lts.h"
#include "ks_binder.h"
#include "utils.h"
#include "gpio_test.h"
#include "iostream"


// для поддержки STL контейнеров, автоматическая конвертация 
// между C++ STL  контейнерами и Python типами (для компаса)
#include <pybind11/stl.h>  

// конвертация между C++ std::function и Python callable объектами (для пинов)
#include <pybind11/functional.h>


namespace py = pybind11;

static std::unique_ptr<OrangePi3LTS> g_board;
static std::unique_ptr<KsBinder> g_binder;

// режимм нумерации пинов
enum class PinNumberingMode {
	NONE, // по умолчанию
	BOARD,
	BCM,
	SUNXI
};

// режим GPIO пина
enum class GpioMode {
	OFF, // по умолчанию
	INPUT,
	OUTPUT
};

// ростояние пина (pinstate или gpiostate?)
enum class PinState {
	LOW,
	HIGH	
};



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


// получение платы
OrangePi3LTS& get_board() {
	if (!g_board) {
		throw std::runtime_error("Board not initialized");	
	}
	return *g_board;										
}

// получение биндера
KsBinder& get_binder() {
	if (!g_binder) {
		throw std::runtime_error("Binder not initialized");
	}
	return *g_binder;
}

// ks_service
namespace ks_service_bindings {

	KompasAPI7::IApplicationPtr get_app() {
		return ksGetApp();
	}

	KompasAPI7::IKompasDocument3DPtr get_active_document_3d() {
		auto app = ksGetApp();
		return ksGetActiveDocument3D(app);
	}

	KompasAPI7::IFeature7Ptr get_feature_by_name(const std::wstring& name) {
		auto app = ksGetApp();
		auto doc = ksGetActiveDocument3D(app);
		return ksGetFeatureByNameInDoc3D(doc, name);
	}

	std::vector<KompasAPI7::IBody7Ptr> get_feature_bodies(const std::wstring& name) {
		auto feature = get_feature_by_name(name);
		return ksGetFeatureBodies(feature);
	}

	void set_body_color(KompasAPI7::IBody7Ptr body, int r, int g, int b) {
		ksSetBodyColor(body, r, g, b);
	}

	void update_bodies_color() {
		auto app = ksGetApp();
		auto doc = ksGetActiveDocument3D(app);
		ksUpdateBodiesColorInDocument(doc);
	}

	bool is_document_assembly() {
		auto app = ksGetApp();
		auto doc = ksGetActiveDocument3D(app);
		return ksGetIsDocAssembly(doc);
	}

}

PYBIND11_MODULE(kopis, m) {
	m.doc() = "KOPIS (Kompas-3D Orange Pi Simulator) Python module";

	// создание capsule и привязка к модулю
	py::capsule capsule = py::capsule(new BoardCapsule(), [](void* ptr) {
		delete static_cast<BoardCapsule*>(ptr);
	});
	m.add_object("_board_capsule", capsule);


	// enum привязки 

	py::enum_<PinNumberingMode>(m, "PinNumberingMode")
		.value("NONE", PinNumberingMode::NONE)
		.value("BOARD", PinNumberingMode::BOARD)
		.value("BCM", PinNumberingMode::BCM)
		.value("SUNXI", PinNumberingMode::SUNXI)
		.export_values();

	py::enum_<GpioMode>(m, "GpioMode")
		.value("OFF", GpioMode::OFF)
		.value("IN", GpioMode::INPUT)
		.value("OUT", GpioMode::OUTPUT)
		.export_values();

	py::enum_<PinState>(m, "PinState")
		.value("LOW", PinState::LOW)
		.value("HIGH", PinState::HIGH)
		.export_values();

	py::enum_<PinType>(m, "PinType")
		.value("GPIO", PinType::GPIO)
		.value("SPECIAL", PinType::SPECIAL)
		.value("POWER", PinType::POWER)
		.value("GROUND", PinType::GROUND)
		.export_values();

	py::enum_<PinMode>(m, "PinMode")
		.value("INPUT", PinMode::INPUT)
		.value("OUTPUT", PinMode::OUTPUT)
		.value("ALT", PinMode::ALT)
		.value("OFF", PinMode::OFF)
		.export_values();

	py::enum_<GpioState>(m, "GpioState")
		.value("LOW", GpioState::LOW)
		.value("HIGH", GpioState::HIGH)
		.export_values();

	// Класс Pin
	py::class_<Pin>(m, "Pin")
		.def("get_board_number", &Pin::getBoardNumber)
		.def("get_name", &Pin::getName)
		.def("get_type", &Pin::getType);

	// Класс GpioPin
	py::class_<GpioPin, Pin>(m, "GpioPin")
		.def("get_soc_name", &GpioPin::getSocName)
		.def("get_gpio_number", &GpioPin::getGpioNumber)
		.def("get_mode", &GpioPin::getMode)
		.def("get_state", &GpioPin::getState)
		.def("set_mode", &GpioPin::setMode)
		.def("set_state", &GpioPin::setState);

	// Класс SpecialPin
	py::class_<SpecialPin, GpioPin>(m, "SpecialPin")
		.def("get_alt_function", &SpecialPin::getAltFunction);

	// Класс PowerPin
	py::class_<PowerPin, Pin>(m, "PowerPin");
	
	// Класс GroundPin
	py::class_<GroundPin, Pin>(m, "GroundPin");

	// Класс OrangePi3LTS
	py::class_<OrangePi3LTS>(m, "OrangePi3LTS")
		.def(py::init<>())
		.def("get_pin_by_board_number", &OrangePi3LTS::getPinByBoardNumber,
			py::return_value_policy::reference)	
		.def("get_pin_by_soc_name", &OrangePi3LTS::getPinBySocName,
			py::return_value_policy::reference)
		.def("get_all_pins", &OrangePi3LTS::getAllPins)
		.def("print_board_pins", &OrangePi3LTS::printBoardPins);
	
	// Класс KsBinder
	py::class_<KsBinder>(m, "KsBinder")
		.def(py::init<OrangePi3LTS&>(), py::arg("board"))
		.def("setup_all_pins", &KsBinder::setupAllPins)
		.def("clear_all_pins", &KsBinder::clearAllPins)
		.def("set_pin_body_color", [](KsBinder& self, const Pin* pin, int r, int g, int b) {
		self.setPinBodyColor(pin, r, g, b);
		}, "Set pin body color", py::arg("pin"), py::arg("r"), py::arg("g"), py::arg("b"));

	//  обертки для Kompas API (COM pointer types)
	py::class_<KompasAPI7::IApplicationPtr>(m, "IApplicationPtr")
		.def("__bool__", [](const KompasAPI7::IApplicationPtr& ptr) {
		return static_cast<bool>(ptr);
		});

	py::class_<KompasAPI7::IKompasDocument3DPtr>(m, "IKompasDocument3DPtr")
		.def("__bool__", [](const KompasAPI7::IKompasDocument3DPtr& ptr) {
		return static_cast<bool>(ptr);
		});

	py::class_<KompasAPI7::IFeature7Ptr>(m, "IFeature7Ptr")
		.def("__bool__", [](const KompasAPI7::IFeature7Ptr& ptr) {
		return static_cast<bool>(ptr);
		})
		.def_property_readonly("name", [](const KompasAPI7::IFeature7Ptr& ptr) -> std::wstring {
		if (ptr) {
			return strUtils::bstrToWStr(ptr->Name);
		}
		return L"";
		});

	py::class_<KompasAPI7::IBody7Ptr>(m, "IBody7Ptr")
		.def("__bool__", [](const KompasAPI7::IBody7Ptr& ptr) {
		return static_cast<bool>(ptr);
			})
		.def_property_readonly("name", [](const KompasAPI7::IBody7Ptr& ptr) -> std::wstring {
		if (ptr) {
			return strUtils::bstrToWStr(ptr->Name);
		}
		return L"";
		});


	// функции для работы с режимами нумерации
	m.def("setmode", [](PinNumberingMode mode) {
		g_numberingMode = mode;
	}, "Set GPIO numbering mode");

	m.def("getmode", []() -> PinNumberingMode {
		return g_numberingMode;
	}, "Get current GPIO numbering mode");

	m.def("setmode", [](PinNumberingMode mode) {
		g_numberingMode = mode;
	}, "Set GPIO numbering mode");

	m.def("getmode", []() -> PinNumberingMode {
		return g_numberingMode;
	}, "Get current GPIO numbering mode");

// функции для работы с пинами
//	m.def("setup", [](int pinNumber, PinMode mode) {
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");
//		}
//
//		//GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
//			pin.setMode(mode);
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to setup pin: ") + e.what());
//		}
//	});
//
//	// перегрузка для типа string (для нахождения по SUNXI)
//	m.def("setup", [](const std::string& socName, PinMode mode) {
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");
//		}
//
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
//			pin.setMode(mode);
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to setup pin: ") + e.what());
//		}
//	}, "Setup pin mode by SoC name", py::arg("soc_name"), py::arg("mode"));
//
//	m.def("output", [](int pinNumber, GpioState state) {
//		//GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");
//		}
//
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
//			pin.setState(state);
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to set output: ") + e.what());
//		}
//
//	}, "Set pin output state", py::arg("pin_number"), py::arg("state"));
//
//	//перегрузка для типа string (для нахождения по SUNXI)
//	m.def("output", [](const std::string& socName, GpioState state) {
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");	
//		}
//
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
//			pin.setState(state);
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to set output: ") + e.what());
//		}
//	}, "Set pin output state by SoC name", py::arg("soc_name"), py::arg("state"));
//
//	m.def("input", [](int pinNumber) -> GpioState {	
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");
//		}
//
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
//			return pin.getState();
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to read input: ") + e.what());
//		}
//	}, "Read pin input state", py::arg("pin_number"));
//
//	m.def("input", [](const std::string& socName) -> GpioState {
//		if (g_numberingMode == PinNumberingMode::NONE) {
//			throw std::runtime_error("GPIO numbering mode is not set");
//		}
//
//		try {
//			GpioPin& pin = static_cast<GpioPin&>(g_board->getPinBySocName(socName));
//			return pin.getState();
//		}
//		catch (const std::exception& e) {
//			throw std::runtime_error(std::string("Failed to read input: ") + e.what());
//		}
//	}, "Read pin input state by SoC name", py::arg("soc_name"));


	// функции для работы с пинами v2
	m.def("setup", [](py::object pin_identifier, PinMode mode) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}

		try {
			GpioPin* pin_ptr = nullptr;

			if (py::isinstance<py::int_>(pin_identifier)) {
				int pinNumber = pin_identifier.cast<int>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
			}
			else if (py::isinstance<py::str>(pin_identifier)) {
				std::string socName = pin_identifier.cast<std::string>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinBySocName(socName));
			}
			else {
				throw std::runtime_error("Pin identifier must be int (board number) or string (SoC name)");
			}

			pin_ptr->setMode(mode);
		}
		catch (const std::exception& e) {
			throw std::runtime_error(std::string("Failed to setup pin: ") + e.what());
		}
		}, "Setup pin mode by board number (int) or SoC name (string)",
		py::arg("pin_identifier"), py::arg("mode"));

	m.def("output", [](py::object pin_identifier, GpioState state) {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}

		try {
			GpioPin* pin_ptr = nullptr;

			if (py::isinstance<py::int_>(pin_identifier)) {
				int pinNumber = pin_identifier.cast<int>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
			}
			else if (py::isinstance<py::str>(pin_identifier)) {
				std::string socName = pin_identifier.cast<std::string>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinBySocName(socName));
			}
			else {
				throw std::runtime_error("Pin identifier must be int (board number) or string (SoC name)");
			}

			pin_ptr->setState(state);
		}
		catch (const std::exception& e) {
			throw std::runtime_error(std::string("Failed to set output: ") + e.what());
		}
		}, "Set pin output state", py::arg("pin_identifier"), py::arg("state"));

	m.def("input", [](py::object pin_identifier) -> GpioState {
		if (g_numberingMode == PinNumberingMode::NONE) {
			throw std::runtime_error("GPIO numbering mode is not set");
		}

		try {
			GpioPin* pin_ptr = nullptr;

			if (py::isinstance<py::int_>(pin_identifier)) {
				int pinNumber = pin_identifier.cast<int>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinByBoardNumber(pinNumber));
			}
			else if (py::isinstance<py::str>(pin_identifier)) {
				std::string socName = pin_identifier.cast<std::string>();
				pin_ptr = &static_cast<GpioPin&>(g_board->getPinBySocName(socName));
			}
			else {
				throw std::runtime_error("Pin identifier must be int (board number) or string (SoC name)");
			}

			return pin_ptr->getState();
		}
		catch (const std::exception& e) {
			throw std::runtime_error(std::string("Failed to read input: ") + e.what());
		}
		}, "Read pin input state", py::arg("pin_identifier"));

	// Функции для ks_service
	m.def("ks_get_app", &ks_service_bindings::get_app, "Get Kompas application instance");

	m.def("ks_get_active_document_3d", &ks_service_bindings::get_active_document_3d, "Get active 3D document");

	m.def("ks_get_feature_by_name", &ks_service_bindings::get_feature_by_name, "Get feature by name", py::arg("name"));

	m.def("ks_get_feature_bodies", &ks_service_bindings::get_feature_bodies, "Get all bodies from feature", py::arg("name"));

	m.def("ks_set_body_color", &ks_service_bindings::set_body_color, "Set body color", py::arg("body"), py::arg("r"), py::arg("g"), py::arg("b"));

	m.def("ks_update_bodies_color", &ks_service_bindings::update_bodies_color, "Update bodies color in document");

	m.def("ks_is_document_assembly", &ks_service_bindings::is_document_assembly, "Check if document is assembly");

	// получение доступа к платe
	m.def("get_board", &get_board, py::return_value_policy::reference,
		"Get the Orange Pi 3 LTS board instance");

	// вывод всех пинов
	m.def("print_pins_table", []() {
		if (g_board) {
			g_board->printBoardPins();
		}
		else {
			throw std::runtime_error("Board not initialized");
		}
	}, "Print board pins table");

	// очистка
	m.def("cleanup", []() {
		// сброс всех пинов в исходное состояние
		if (g_board) {
			auto pins = g_board->getAllPins();
			for (auto& pin_ref : pins) {
				Pin& pin = pin_ref.get();
				if (pin.getType() == PinType::GPIO || pin.getType() == PinType::SPECIAL) {
					GpioPin& gpio_pin = static_cast<GpioPin&>(pin);
					try {
						gpio_pin.setMode(PinMode::OFF);
						if (gpio_pin.getMode() == PinMode::OUTPUT) {
							gpio_pin.setState(GpioState::LOW);
						}
					}
					catch (...) {
						// игнорируем ошибки при cleanup
					}
				}
			}
		}
	}, "Cleanup all pins");
}