#pragma once

#include <string>
#include <stdexcept>

// Перечисление типов пинов
enum class PinType {
	GPIO,
	SPECIAL, // (I2C, UART, SPI, PWM)
	POWER,
	GROUND
};

// Перечисление режимов для GPIO и SPECIAL пинов 
enum class PinMode {
	INPUT,   // Режим чтения
	OUTPUT,  // Режим записи
	ALT,     // Режим альтернативной функции (I2C, UART, SPI, PWM). Только для SPECIAL пинов
	OFF      // Неактивен (по умолчанию)
};

// Перечисление состояний пинов GPIO или SPECIAL в режиме OUTPUT
enum class GpioState {
	LOW,     // Выкл
	HIGH     // Вкл
};


// Общий родительский класс для всех пинов
class Pin {
public:
	// Конструктор класса и инициализация его полей
	Pin(int boardNumber_, const std::string& name_)
		: boardNumber(boardNumber_), name(name_) { }

	// Виртуальный деструктор для базового класса
	virtual ~Pin() = default;

	// Получить физический номер пина на плате
	int getBoardNumber() const { 
		return boardNumber;
	}

	// Получить имя пина
	std::string getName() const {
		return name;
	}

	// Чисто виртуальный метод, который обязует все классы-наследники
	// возвращать свой тип пина (GPIO, POWER, GROUND, SPECIAL)
	virtual PinType getType() const = 0;

protected:
	int boardNumber;  // Физический номер пина на плате (1-26)
	std::string name; // Имя пина на плате
};


// Производный класс для GPIO пинов
class GpioPin : public Pin {
public:
	GpioPin(int boardNumber_, const std::string& name_, const std::string& socName_, int gpioNumber_)
		: Pin(boardNumber_, name_), // Инициализация членов базового класса
		socName(socName_),
		gpioNumber(gpioNumber_),
		// По умолчанию пин будет инициализироваться с режимом OFF и состоянием LOW
		mode(PinMode::OFF),
		state(GpioState::LOW) { }

	// Получить имя контакта на сокете
	std::string getSocName() const {
		return socName;
	}

	// Получить номер GPIO
	int getGpioNumber() const {
		return gpioNumber;
	}

	// Получить текущий режим работы пина
	PinMode getMode() const {
		return mode;
	}

	// Установить режим работы пина (только INPUT или OUTPUT)
	virtual void setMode(PinMode newMode) {
		if (newMode == PinMode::ALT) {
			throw std::logic_error("ALT mode is not supported on plain GPIO pins");
		}
		mode = newMode;
	}

	// Установить состояние пина (LOW или HIGH), только если в режиме OUTPUT
	void setState(GpioState newState) {
		if (mode != PinMode::OUTPUT) {
			throw std::logic_error("Cannot write the state when pin is not in OUTPUT mode");
		}
		else {
			state = newState;
		}
	}

	// Получить текущее состояние пина
	virtual GpioState getState() const {
		return state;
	}

	// Вернуть тип пина
	PinType getType() const override {
		return PinType::GPIO;
	}

protected:
	std::string socName;  // Имя контакта на сокете (PD26, PL10, PH4 и т.п.)
	int gpioNumber;       // Номер GPIO
	PinMode mode;         // Режим пина
	GpioState state;      // Состояние пина
};


// Производный класс для SPECIAL пинов. Наследуется от GPIO
// Может работать либо как GPIO пин, либо как ALT пин
class SpecialPin : public GpioPin {
public:
	SpecialPin(int boardNumber_, const std::string& name_,
	const std::string& socName_, int gpioNumber_, const std::string& altFunction_)
		: GpioPin(boardNumber_, name_, socName_, gpioNumber_),
		altFunction(altFunction_) { }

	// Установить режим работы пина
	virtual void setMode(PinMode newMode) override {
		mode = newMode;
	}

	// Получить текущее состояние пина
	virtual GpioState getState() const override {
		if (mode == PinMode::ALT) {
			throw std::logic_error("Pin state unavailable in ALT mode");
		}
		else {
			return state;
		}
	}

	// Получить ALT-функцию пина
	std::string getAltFunction() const {
		return altFunction;
	}

	// Вернуть тип пина
	PinType getType() const override {
		return PinType::SPECIAL;
	}

private:
	std::string altFunction; // ALT-функция пина
};


// Производный класс для пинов питания
class PowerPin : public Pin {
public:
	PowerPin (int boardNumber_, const std::string& name_)
		: Pin(boardNumber_, name_) { }

	// Вернуть тип пина
	PinType getType() const override {
		return PinType::POWER;
	}
};


// Производный класс для пинов GND
class GroundPin : public Pin {
public:
	GroundPin (int boardNumber_, const std::string& name_)
		: Pin(boardNumber_, name_) { }

	// Вернуть тип пина
	PinType getType() const override {
		return PinType::GROUND;
	}
};