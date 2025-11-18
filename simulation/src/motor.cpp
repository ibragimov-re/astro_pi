#include "motor.h"
#include "utils.h"
#include <iomanip>
#include <cmath>


Motor::Motor(const std::wstring& name_)
    : name(name_), shaftAngle(0.0f) {
}


std::wstring Motor::getName() const {
    return name;
}


void Motor::rotateShaftAngle(double angle, int speed) {
    
    if (speed <= 0) return;
    
    bool isClockwise = angle >= 0;

    // Привести угол к абсолютному значению
    angle = std::fabs(angle);

    // Привести угол к диапазону [0...360]
    angle = fmod(angle, 360.0);

    if (angle == 0.0) return;

    double step = static_cast<double>(speed);
    int iterations = static_cast<int>(angle / step);
    double remainderAngle = fmod(angle, step);

    double direction = isClockwise ? 1.0 : -1.0;

    for (int i = 0; i < iterations; ++i) {
        shiftAngle(step * direction);
    }

    if (remainderAngle != 0.0) {
        shiftAngle(remainderAngle * direction);
    }
}


void Motor::shiftAngle(double angle) {
    setShaftAngle(shaftAngle + angle);
}


void Motor::setShaftAngle(double angle) {
    shaftAngle = normalizeAngle(angle);
    notifyChangeAngle();
}


double Motor::normalizeAngle(double angle) {
    angle = fmod(angle, 360.0);

    return (angle > 0.0) ? angle : angle + 360.0;
}


double Motor::getShaftAngle() const {
    return shaftAngle;
}


void Motor::resetShaftAngle() {
    setShaftAngle(0);
}


void Motor::setOnChangeCallback(AngleChangeCallback cb) const {
    onChange = std::move(cb);
}


void Motor::notifyChangeAngle() const {
    // Если подчисчик установлен - вызвать его, передавая текущий пин
    if (onChange) onChange(this);
}