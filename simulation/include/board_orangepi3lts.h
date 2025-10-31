#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include "pin.h"

class OrangePi3LTS {
public:
	OrangePi3LTS(); // Конструктор платы

	// Запрещаем копирование, т.к. вектор содержит unique_ptr		//-
	OrangePi3LTS(const OrangePi3LTS&) = delete;						//-
	OrangePi3LTS& operator=(const OrangePi3LTS&) = delete;			//-
																	//-
	// Разрешаем перемещение										//-
	OrangePi3LTS(OrangePi3LTS&&) noexcept = default;				//-
	OrangePi3LTS& operator=(OrangePi3LTS&&) noexcept = default;		//-
																	//-
	
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