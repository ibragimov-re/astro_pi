#include "ks_binder.h"
#include "pin.h"


KsBinder::KsBinder(Assembly& assembly_)
	: assembly(assembly_), board(assembly.getBoard())
{
    try {
        // Инициализация COM
        CoInitialize(NULL);

        auto ksApp = ksGetApp();
        ksDoc3D = ksGetActiveDocument3D(ksApp);

        std::wstring boardPartName = L"#OrangePi3LTS";
        auto boardFeature = ksGetFeatureByNameInDoc3D(ksDoc3D, boardPartName);
        consoleUtils::printMessage(L"[OK] Find board part: " + strUtils::bstrToWStr(boardFeature->Name) + L"\n");

        auto bodiesVec = ksGetFeatureBodies(boardFeature);
        auto pinsVec = board.getAllPins();

        for (auto& pinRef : pinsVec) {
            Pin& pin = pinRef.get();

            int num = pin.getBoardNumber();
            std::wstring bodyNameInCAD = L"#PIN" + std::to_wstring(num);

            for (auto& body : bodiesVec) {
                auto bodyName = strUtils::bstrToWStr(body->Name);

                // Если имена совпадают, то связываем и добавляем в словарь указатель на пин симулятора
                // и указатель на тело пина в Компас-3D
                if (bodyName == bodyNameInCAD) {
                    pinBodiesMap[&pin] = body;
                }
            }
        }

        isDocAssembly = ksIsDocAssembly(ksDoc3D);

        setupAllPins();

        setupAllMotors();
    }
    catch (const std::exception& ex) {
        throw std::runtime_error(ex.what());
    }
}

KsBinder::~KsBinder() {
    clearAllPins();

    // Освобождение COM
    CoUninitialize();
}


void KsBinder::setupAllPins() {
    for (auto& [pin, body] : pinBodiesMap) {
        setPinBodyColorByModeAndState(pin, body);

        // Установка лямбда-функции, которая будет выполняться при обновлении режима или состояния пина
        pin->setOnChangeCallback([this, &pin, body](const Pin* changedPin) {
            this->setPinBodyColorByModeAndState(pin, body);
            ksUpdateAllBodiesColorInAssembly(ksDoc3D);
            });
    }

    // Обновление цвета у всех тел после задания цветов для всех пинов
    // это позволяет ускорить инициализацию платы в сборке
    if (isDocAssembly) {
        ksUpdateAllBodiesColorInAssembly(ksDoc3D);
    }
}


void KsBinder::setPinBodyColorByModeAndState(const Pin* pin, KompasAPI7::IBody7Ptr) {
    switch (pin->getType()) {
    case PinType::SPECIAL:
    case PinType::GPIO: {
        setGpioAndSpecialPinBodyColor(static_cast<const GpioPin*>(pin));
        break;
    }

    case PinType::GROUND: {
        setPinBodyColor(pin, 180, 90, 30); // Коричневый
        break;
    }

    case PinType::POWER: {
        setPinBodyColor(pin, 255, 255, 0); // Желтый
        break;
    }
    }
}


void KsBinder::setGpioAndSpecialPinBodyColor(const GpioPin* pin) {
    int num = pin->getBoardNumber();

    switch (pin->getMode()) {
    case GpioMode::OFF:
        setPinBodyColor(pin, 70, 70, 70); // Серый
        break;

    case GpioMode::OUTPUT: {
        auto state = pin->getState();
        if (state == GpioState::LOW)
            setPinBodyColor(pin, 255, 0, 0); // Красный
        else
            setPinBodyColor(pin, 0, 255, 0); // Зеленый
        break;
    }

    case GpioMode::INPUT:
        setPinBodyColor(pin, 0, 255, 255); // Голубой
        break;

    case GpioMode::ALT:
        setPinBodyColor(pin, 200, 0, 255); // Фиолетовый
        break;
    }
}


void KsBinder::clearAllPins() {
    for (const auto& [pin, body] : pinBodiesMap) {
        setPinBodyColor(pin, 200, 200, 200); // Белый
    }

    // Обновление цвета у всех тел после задания цветов для всех пинов
    // это позволяет ускорить очистку платы в сборке
    if (isDocAssembly) {
        ksUpdateAllBodiesColorInAssembly(ksDoc3D);
    }
}


void KsBinder::setPinBodyColor(const Pin* pin, int r, int g, int b) {
    auto it = pinBodiesMap.find(pin);
    if (it != pinBodiesMap.end()) {
        auto body = it->second;
        ksSetBodyColor(body, r, g, b);
    }
}


void KsBinder::setupAllMotors() {
    for (auto& motorRef : assembly.getAllMotors()) {
        Motor& motor = motorRef.get();
        std::wstring motorName = motor.getName();

        KompasAPI7::IFeature7Ptr motorFeature = ksGetFeatureByNameInDoc3D(ksDoc3D, motorName);
        KompasAPI7::IPart7Ptr motorPart = motorFeature;

        motorAssembliesMap[&motor] = motorPart;

        // Установка лямбда-функции, которая будет выполняться при обновлении угла вала мотора
        motor.setOnChangeCallback([this, &motor, motorPart](const Motor* changedPin) {
            ksSetVariableExpressionInPart(motorPart, L"ShaftAngle", std::to_wstring(motor.getShaftAngle()));
            ksRebuildDocument(ksDoc3D);
            });

        consoleUtils::printMessage(L"[OK] Find motor assembly: " + motorName + L"\n");
    }
}