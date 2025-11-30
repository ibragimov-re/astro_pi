cmake_minimum_required(VERSION 3.8)

project(KOPIS VERSION 1.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(KOMPAS_SDK_PATH "$ENV{KOMPAS_SDK}")
set(KOMPAS_TLBS_PATH "${KOMPAS_SDK_PATH}lib")
message(STATUS "Kompas TLBs path: ${KOMPAS_TLBS_PATH}")

# Задание конкретной версии python, под которую будет собран pybind11-модуль
find_package(Python3 3.13 EXACT REQUIRED COMPONENTS Interpreter Development)

# Добавить pybind11 как подмодуль
add_subdirectory(extern/pybind11)

# Создать Python модуль
pybind11_add_module(kopis
	"src/main.cpp"
	"src/assembly.cpp"
	"src/board_orangepi3lts.cpp"
	"src/pin.cpp"
	"src/motor.cpp"
	"src/ks_service.cpp"
	"src/ks_binder.cpp"
	"tests/gpio_test.cpp"
)

# Передача версии проекта из CMake в C++ код для использования как версии Python-модуля
target_compile_definitions(kopis PRIVATE KOPIS_VERSION="${PROJECT_VERSION}")

target_include_directories(kopis PRIVATE
	"include"
	"tests"
	${KOMPAS_TLBS_PATH} # Для импорта .tlb файлов Kompas API и геренерации из них .tlh, .tli файлов
)

target_precompile_headers(kopis PRIVATE include/pch.h)

target_compile_definitions(kopis PRIVATE UNICODE _UNICODE)


# ========================================================
# Копирование сгенерированных файлов .tlh и .tli в корень
# проекта после сборки, чтобы IDE их корректно находила
# ========================================================
set(ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "Root dir path: ${CMAKE_CURRENT_SOURCE_DIR}")
set(BUILD_DIR "${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/kopis.dir")
message(STATUS "Build dir path: ${BUILD_DIR}")

add_custom_command(TARGET kopis POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E echo "Copy generated .tlh/.tli files to project root"

    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BUILD_DIR}/kAPI7.tlh" "${ROOT_DIR}/"
	COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BUILD_DIR}/kAPI7.tli" "${ROOT_DIR}/"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BUILD_DIR}/ksConstants.tlh" "${ROOT_DIR}/"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BUILD_DIR}/ksConstants3D.tlh" "${ROOT_DIR}/"
)