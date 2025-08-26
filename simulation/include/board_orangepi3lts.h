#pragma once

#include <string>
#include <vector>
#include <memory>
#include "pin.h"

class OrangePi3LTS {
public:
	OrangePi3LTS(); // Конструктор платы

	// Найти пин по физическому номеру
	Pin& getPinByBoardNumber(int boardNumber) const;

	// Найти пин по имени сокета
	Pin& getPinBySocName(const std::string& socName) const;

	// Получить все пины
	std::vector<std::reference_wrapper<Pin>> getAllPins() const;

	// Вывод таблицы с пинами платы
	void printBoardPins() const;

private:
	// Контейнер с умными указателями на пины
	std::vector<std::unique_ptr<Pin>> pins;
};