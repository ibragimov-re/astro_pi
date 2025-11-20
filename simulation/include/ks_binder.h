#pragma once

#include <map>
#include "board_orangepi3lts.h"
#include "assembly.h"
#include "pin.h"
#include "motor.h"
#include "ks_service.h"


class KsBinder {
public:
    explicit KsBinder(Assembly& assembly);
    ~KsBinder();

    // Обновить цвет всех пинов и добавить обработчик изменения
    // состояния и режима для каждого пина через callback функцию
    void setupAllPins();

    // Очистить все пины
    void clearAllPins(); 

    // Задать цвет пина по его режиму и состоянию
    void setPinBodyColorByModeAndState(const Pin* pin, KompasAPI7::IBody7Ptr);

    // Задать цвет пина
    void setPinBodyColor(const Pin* pin, int r, int g, int b);

    // Найти и настроить моторы
    void setupAllMotors();

private:
    // Задать цвет GPIO или SPECIAL пину по его режиму и состоянию
    void setGpioAndSpecialPinBodyColor(const GpioPin* pin);

    // Словарь с указателями на пины симулятора и указателями на тела пинов в Компас-3D
    std::map<const Pin*, KompasAPI7::IBody7Ptr> pinBodiesMap;

    // Словарь с указателями на моторы симулятора и указателями на сборки моторов в Компас-3D
    std::map<const Motor*, KompasAPI7::IPart7Ptr> motorAssembliesMap;

    Assembly& assembly;
    const OrangePi3LTS& board;
    KompasAPI7::IKompasDocument3DPtr ksDoc3D;
    bool isDocAssembly = true;
};