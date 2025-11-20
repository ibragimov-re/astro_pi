#include "assembly.h"

Assembly::Assembly() {
    motors.emplace_back(std::make_unique<Motor>(L"#Nema17HS8401_Horizontal"));
    motors.emplace_back(std::make_unique<Motor>(L"#Nema17HS8401_Vertical"));
}

const OrangePi3LTS& Assembly::getBoard() const {
    return board;
}

std::vector<std::reference_wrapper<Motor>> Assembly::getAllMotors() const {
    std::vector<std::reference_wrapper<Motor>> result;
    for (const auto& motor : motors) {
        result.push_back(*motor); // Разыменовать указатель и добавить ссылку на пин в вектор
    }
    return result;
}

Motor& Assembly::getMotor(std::wstring motorName) {
    for (auto& motor : motors) {
        if (motor->getName() == motorName) {
            return *motor;
        }
    }
    throw std::out_of_range("No motor with this name");
}