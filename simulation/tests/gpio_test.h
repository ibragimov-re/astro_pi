#pragma once
#include "assembly.h"

namespace tests {
    // Запустить тестовую программу с изменением GPIO пинов
    void RunGpioPinsTest(Assembly& assembly);

    // Запустить тестовую программу с моторами
    void RunMotorsTest(Assembly& assembly);
}