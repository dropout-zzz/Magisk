# https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html#cross-compiling-for-android-with-the-ndk

set(CMAKE_SYSTEM_NAME Android)
set(CMAKE_SYSTEM_VERSION 23)  # sync with upstream
set(CMAKE_ANDROID_ARCH_ABI arm64-v8a)

# https://developer.android.com/ndk/guides/cpp-support
set(CMAKE_ANDROID_STL_TYPE c++_static)
