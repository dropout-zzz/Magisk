add_subdirectory(corrosion)

if(ANDROID)
  set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

  set(LZ4_BUILD_CLI OFF)
  set(LZ4_BUILD_LEGACY_LZ4C OFF)

  add_subdirectory(lz4/build/cmake EXCLUDE_FROM_ALL)
endif()

add_library(cxxrs STATIC
  cxx-rs/src/cxx.cc)
