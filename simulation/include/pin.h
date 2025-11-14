#pragma once

#include <string>
#include <stdexcept>
#include <functional>

// Перечисление типов пинов
enum class PinType {
	GPIO,
	SPECIAL, // (I2C, UART, SPI, PWM)
	POWER,
	GROUND
};

// Перечисление режимов для GPIO и SPECIAL пинов 
enum class GpioMode {
	INPUT,   // Режим чтения
	OUTPUT,  // Режим записи
	ALT,     // Режим альтернативной функции (I2C, UART, SPI, PWM). Только для SPECIAL пинов
	OFF      // Неактивен (по умолчанию)
};

// Перечисление состояний пинов GPIO или SPECIAL в режиме OUTPUT
enum class GpioState {
	LOW,     // Выкл (по умолчанию)
	HIGH     // Вкл
};


// Общий родительский класс для всех пинов
class Pin {
public:
	// Конструктор класса
	Pin(int boardNumber_, const std::string& name_);

	// Виртуальный деструктор для базового класса
	virtual ~Pin();

	// Получить физический номер пина на плате
	int getBoardNumber() const;

	// Получить имя пина
	std::string getName() const;

	// Получить тип пина
	virtual PinType getType() const = 0;

	// Функция обратного вызова (callback), вызываемая при изменении состояния или режима пина
	using StateOrModeChangeCallback = std::function<void(const Pin*)>;

	// Устанавливает callback, который будет вызван при изменении состояния или режима пина
	void setOnChangeCallback(StateOrModeChangeCallback cb) const;

protected:
	// Вызывает callback, уведомляя подписчика (функцию в onChange) о том, что состояние или режим пина изменились
	void notifyChangeStateOrMode() const;

	int boardNumber;  // Физический номер пина на плате (1-26)
	std::string name; // Имя пина на плате

private:
	// Callback, вызываемый при изменении состояния или режима пина.
	// Отмечен как mutable, чтобы его можно было устанавливать из const методов,
	// т.к. установка callback не меняет логическое состояние пина.
	mutable StateOrModeChangeCallback onChange;
};


// Производный класс для GPIO пинов
class GpioPin : public Pin {
public:
	GpioPin(int boardNumber_, const std::string& name_, const std::string& socName_, int gpioNumber_);

	// Получить имя контакта на сокете
	std::string getSocName() const;

	// Получить номер GPIO
	int getGpioNumber() const;

	// Получить текущий режим работы пина
	GpioMode getMode() const;

	// Получить текущее состояние пина
	virtual GpioState getState() const;

	// Получить тип пина
	PinType getType() const;

	// Установить режим работы пина (только INPUT или OUTPUT)
	virtual void setMode(GpioMode newMode);

	// Установить состояние пина (LOW или HIGH), только если в режиме OUTPUT
	void setState(GpioState newState);

protected:
	std::string socName;  // Имя контакта на сокете (PD26, PL10, PH4 и т.п.)
	int gpioNumber;       // Номер GPIO
	GpioMode mode;         // Режим пина
	GpioState state;      // Состояние пина
};


// Производный класс для SPECIAL пинов. Наследуется от GPIO
// Может работать либо как GPIO пин, либо как ALT пин
class SpecialPin : public GpioPin {
public:
	SpecialPin(int boardNumber_, const std::string& name_,
		const std::string& socName_, int gpioNumber_, const std::string& altFunction_);

	// Получить текущее состояние пина
	virtual GpioState getState() const override;

	// Получить тип пина
	PinType getType() const override;

	// Получить ALT-функцию пина
	std::string getAltFunction() const;

	// Установить режим работы пина
	virtual void setMode(GpioMode newMode);

private:
	std::string altFunction; // ALT-функция пина
};


// Производный класс для пинов питания
class PowerPin : public Pin {
public:
	PowerPin(int boardNumber_, const std::string& name_);

	// Получить тип пина
	PinType getType() const override;
};


// Производный класс для пинов GND
class GroundPin : public Pin {
public:
	GroundPin(int boardNumber_, const std::string& name_);

	// Получить тип пина
	PinType getType() const override;
};