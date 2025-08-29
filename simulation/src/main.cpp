#include "board_orangepi3lts.h"

int main() {

    // Тестовый код с изменением режима, состояния пинов и печатью общей таблицы

    OrangePi3LTS board;

    GpioPin& pin12 = static_cast<GpioPin&>(board.getPinByBoardNumber(12));
    pin12.setMode(PinMode::OUTPUT);
    pin12.setState(GpioState::HIGH);

    GpioPin& pin19 = static_cast<SpecialPin&>(board.getPinByBoardNumber(19));
    pin19.setMode(PinMode::ALT);
    GpioPin& pin21 = static_cast<SpecialPin&>(board.getPinByBoardNumber(21));
    pin21.setMode(PinMode::ALT);
    GpioPin& pin23 = static_cast<SpecialPin&>(board.getPinByBoardNumber(23));
    pin23.setMode(PinMode::ALT);

    GpioPin& pin15 = static_cast<GpioPin&>(board.getPinByBoardNumber(15));
    pin15.setMode(PinMode::INPUT);

    board.printBoardPins();

    return 0;
}