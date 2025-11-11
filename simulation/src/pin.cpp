#include "pin.h"


// =================== Pin ===================
Pin::Pin(int boardNumber_, const std::string& name_)
	: boardNumber(boardNumber_), name(name_) {
}

Pin::~Pin() = default;

int Pin::getBoardNumber() const { return boardNumber; }
std::string Pin::getName() const { return name; }

void Pin::setOnChangeCallback(StateOrModeChangeCallback cb) const {
	onChange = std::move(cb);
}

void Pin::notifyChangeStateOrMode() const {
	// Если подчисчик установлен - вызвать его, передавая текущий пин
	if (onChange) onChange(this);
}


// =================== GpioPin ===================
GpioPin::GpioPin(int boardNumber_, const std::string& name_, const std::string& socName_, int gpioNumber_)
	: Pin(boardNumber_, name_), // Инициализация членов базового класса
	socName(socName_),
	gpioNumber(gpioNumber_),
	// По умолчанию пин будет инициализироваться с режимом OFF и состоянием LOW
	mode(GpioMode::OFF),
	state(GpioState::LOW) {
}

std::string GpioPin::getSocName() const { return socName; }
int GpioPin::getGpioNumber() const { return gpioNumber; }
GpioMode GpioPin::getMode() const { return mode; }
GpioState GpioPin::getState() const { return state; }
PinType GpioPin::getType() const { return PinType::GPIO; }

void GpioPin::setMode(GpioMode newMode) {
	if (newMode == GpioMode::ALT) {
		throw std::logic_error("ALT mode is not supported on plain GPIO pins");
	}
	mode = newMode;
	notifyChangeStateOrMode();
}

void GpioPin::setState(GpioState newState) {
	if (mode != GpioMode::OUTPUT) {
		throw std::logic_error("Cannot write the state when pin is not in OUTPUT mode");
	}
	else {
		state = newState;
		notifyChangeStateOrMode();
	}
}


// =================== SpecialPin ===================
SpecialPin::SpecialPin(int boardNumber_, const std::string& name_,
	const std::string& socName_, int gpioNumber_, const std::string& altFunction_)
	: GpioPin(boardNumber_, name_, socName_, gpioNumber_),
	altFunction(altFunction_) {
}

GpioState SpecialPin::getState() const {
	if (mode == GpioMode::ALT) {
		throw std::logic_error("Pin state unavailable in ALT mode");
	}
	else {
		return state;
	}
}

PinType SpecialPin::getType() const { return PinType::SPECIAL; }
std::string SpecialPin::getAltFunction() const { return altFunction; }

void SpecialPin::setMode(GpioMode newMode) {
	mode = newMode;
	notifyChangeStateOrMode();
}


// =================== PowerPin ===================
PowerPin::PowerPin(int boardNumber_, const std::string& name_)
	: Pin(boardNumber_, name_) {
}

PinType PowerPin::getType() const { return PinType::POWER; }


// =================== GroundPin ===================
GroundPin::GroundPin(int boardNumber_, const std::string& name_)
		: Pin(boardNumber_, name_) { }

PinType GroundPin::getType() const {
	return PinType::GROUND;
}