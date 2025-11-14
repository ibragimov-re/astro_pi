#include "ks_binder.h"
#include "pin.h"


KsBinder::KsBinder(OrangePi3LTS& board_)
	: board(board_)
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
        setupAllPins();

        isDocAssembly = ksGetIsDocAssembly(ksDoc3D);
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
        setPinBodyColor(pin, body);

        pin->setOnChangeCallback([this, pin, body](const Pin* changedPin) {
            this->setPinBodyColor(pin, body);
            });
    }
}


void KsBinder::setPinBodyColor(const Pin* pin, KompasAPI7::IBody7Ptr) {
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
}


void KsBinder::setPinBodyColor(const Pin* pin, int r, int g, int b) {
    auto it = pinBodiesMap.find(pin);
    if (it != pinBodiesMap.end()) {
        auto body = it->second;
        ksSetBodyColor(body, r, g, b);

        // Если сборка, то принудительно обновить цвет всех тел для корректного отображения цвета
        if (isDocAssembly) {
            ksUpdateBodiesColorInDocument(ksDoc3D);
        }
    }
}