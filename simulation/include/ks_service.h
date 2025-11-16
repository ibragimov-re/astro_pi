#pragma once

#include "pch.h"
#include <stdexcept>
#include <vector>
#include "utils.h"


// Получить интерфейс приложение
KompasAPI7::IApplicationPtr ksGetApp();

// Получить активный 3D документ
KompasAPI7::IKompasDocument3DPtr ksGetActiveDocument3D(KompasAPI7::IApplicationPtr kompasApp);

// Получить объект по имени из дерева в 3D документе
KompasAPI7::IFeature7Ptr ksGetFeatureByNameInDoc3D(KompasAPI7::IKompasDocument3DPtr doc3d, const std::wstring& name);

// Получить у объекта из дерева все тела 
std::vector<KompasAPI7::IBody7Ptr> ksGetFeatureBodies(KompasAPI7::IFeature7Ptr feature);

// Установить цвет тела
void ksSetBodyColor(KompasAPI7::IBody7Ptr body, int r, int g, int b);

// Обновить цвет тела в сборке
void ksUpdateAllBodiesColorInAssembly(KompasAPI7::IKompasDocument3DPtr doc3d);

// Является ли документ сборкой
bool ksIsDocAssembly(KompasAPI7::IKompasDocument3DPtr doc3d);

// Установить переменную по имени
void ksSetVariableExpressionInPart(KompasAPI7::IPart7Ptr part, std::wstring variableName, std::wstring expression);

// Перестроить документ
void ksRebuildDocument(KompasAPI7::IKompasDocument3DPtr doc3d);