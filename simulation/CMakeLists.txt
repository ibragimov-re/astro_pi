cmake_minimum_required(VERSION 3.8)

project(KOPIS VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SOURCES
	src/main.cpp
	src/board_orangepi3lts.cpp
)

set(HEADERS
	include/board_orangepi3lts.h
	include/pin.h
)

add_executable(Kopis ${SOURCES} ${HEADERS})
target_include_directories(Kopis PRIVATE include)