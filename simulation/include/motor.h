#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>


class Motor {
public:
	Motor(const std::wstring& name_);

	// Получить имя мотора
	std::wstring getName() const;

	// Вращать вал мотора на заданный угол и скорость
	void rotateShaftAngle(double angle, int speed);

	// Установить угол порота вала
	void setShaftAngle(double angle);

	// Получить угол поворота вала
	double getShaftAngle() const;

	// Функция обратного вызова (callback), вызываемая при изменении угла вала мотора
	using AngleChangeCallback = std::function<void(const Motor*)>;

	// Устанавливает callback, который будет вызван при изменении угла вала мотора
	void setOnChangeCallback(AngleChangeCallback cb) const;

protected:
	std::wstring name; // Имя мотора

	// Вызывает callback, уведомляя подписчика (функцию в onChange) о том, что состояние или режим пина изменились
	void notifyChangeAngle() const;

private:
	// Сместить угол
	void shiftAngle(double angle);

	double normalizeAngle(double angle);

	// Текущий угол поворота вала
	double shaftAngle;

	// Callback, вызываемый при изменении изменении угла вала мотора.
	// Отмечен как mutable, чтобы его можно было устанавливать из const методов,
	// т.к. установка callback не меняет угол мотора.
	mutable AngleChangeCallback onChange;
};