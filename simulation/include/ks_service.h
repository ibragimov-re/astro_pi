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

// Обновить цвет тел в сборке
void ksUpdateBodiesColorInDocument(KompasAPI7::IKompasDocument3DPtr doc3d);

// Является ли документ сборкой
bool ksGetIsDocAssembly(KompasAPI7::IKompasDocument3DPtr doc3d);