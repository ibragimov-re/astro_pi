#pragma once

#include <map>
#include "board_orangepi3lts.h"
#include "ks_service.h"


class KsBinder {
public:
    explicit KsBinder(OrangePi3LTS& board);
    ~KsBinder();

    // Обновить цвет всех пинов и добавить обработчик изменения
    // состояния и режима для каждого пина через callback функцию
    void setupAllPins();

    void setPinBodyColor(const Pin* pin, KompasAPI7::IBody7Ptr);

    // Очистить все пины
    void clearAllPins(); 

    // Задать цвет пина
    void setPinBodyColor(const Pin* pin, int r, int g, int b);

private:
    // Задать цвет GPIO или SPECIAL пину по его режиму и состоянию
    void setGpioAndSpecialPinBodyColor(const GpioPin* pin);

    // Словарь с указателями на пины симулятора и указателями на тела пинов в Компас-3D
    std::map<const Pin*, KompasAPI7::IBody7Ptr> pinBodiesMap;

    OrangePi3LTS& board;
    KompasAPI7::IKompasDocument3DPtr ksDoc3D;
    bool isDocAssembly = false;
};