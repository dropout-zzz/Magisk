set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/base-rs.cpp PROPERTIES GENERATED TRUE)

add_library(basecpp STATIC
  base.cpp
  base-rs.cpp)
if(ANDROID OR LINUX OR CYGWIN)
  set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/base-linuxlike-rs.cpp PROPERTIES GENERATED TRUE)
  target_sources(basecpp PRIVATE base-linuxlike-rs.cpp)
endif()
target_compile_definitions(basecpp PRIVATE
  -DNO_FLAGS_H)
target_include_directories(basecpp PUBLIC
  include)
