cmake_minimum_required(VERSION 3.8)

project(KOPIS VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(KOMPAS_SDK_PATH "$ENV{KOMPAS_SDK}")
set(KOMPAS_TLBS_PATH "${KOMPAS_SDK_PATH}lib")
message(STATUS "Kompas TLBs path: ${KOMPAS_TLBS_PATH}")

# Добавить pybind11 как подмодуль
add_subdirectory(extern/pybind11)

# Создать Python модуль
pybind11_add_module(kopis
	"src/main.cpp"
	"src/board_orangepi3lts.cpp"
	"src/pin.cpp"
	"src/ks_service.cpp"
	"src/ks_binder.cpp"
	"tests/gpio_test.cpp"
)

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