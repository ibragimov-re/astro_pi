#pragma once

#include "board_orangepi3lts.h"
#include "motor.h"

class Assembly {
public:
	Assembly();

	//Получить плату
	const OrangePi3LTS& getBoard() const;

	// Получить все моторы
	std::vector<std::reference_wrapper<Motor>> getAllMotors() const;

	// Получить мотор по имени
	Motor& getMotor(std::wstring motorName);

private:
	const OrangePi3LTS board;

	// Контейнер с умными указателями на моторы
	std::vector<std::unique_ptr<Motor>> motors;
};