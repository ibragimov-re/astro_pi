cmake_minimum_required(VERSION 3.8)

# Имя проекта, версия и язык
project(KOPIS VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Указать исходники в переменной SOURCES
set(SOURCES
	src/main.cpp
	src/board_orangepi3lts.cpp
)

# Указать заголовочные файлы в переменной HEADERS
set(HEADERS
	include/board_orangepi3lts.h
	include/pin.h
)

# Создать исполняемый файл из указанных исходников
add_executable(Kopis ${SOURCES} ${HEADERS})

# Указать путь для поиска заголовков при сборке
target_include_directories(Kopis PRIVATE include)