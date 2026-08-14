cmake_minimum_required(VERSION 4.2.0)
project(Magisk LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)  # sync with upstream
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# we don't use this.
set(CMAKE_CXX_SCAN_FOR_MODULES OFF)

if(CYGWIN)
  string(APPEND CMAKE_CXX_FLAGS " -D_GNU_SOURCE")
endif()

if(NOT ANDROID)
  cmake_pkg_config(IMPORT liblz4 REQUIRED)
endif()

add_subdirectory(native/src)

install(TARGETS magiskbootcpp)
