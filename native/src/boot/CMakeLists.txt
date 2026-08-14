set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/boot-rs.cpp PROPERTIES GENERATED TRUE)

add_executable(magiskbootcpp
  boot-rs.cpp
  bootimg.cpp)
target_link_libraries(magiskbootcpp
  cxxrs
  basecpp
  magiskboot)  # the imported Rust component has no suffix.
if(ANDROID)
  target_link_libraries(magiskbootcpp lz4_static)
else()
  target_link_libraries(magiskbootcpp PkgConfig::liblz4)
endif()
set_target_properties(magiskbootcpp PROPERTIES OUTPUT_NAME magiskboot)
