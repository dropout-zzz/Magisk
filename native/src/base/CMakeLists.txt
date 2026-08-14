set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/base-rs.cpp PROPERTIES GENERATED TRUE)

add_library(basecpp STATIC
  base.cpp
  base-rs.cpp)
target_compile_definitions(basecpp PRIVATE
  -DNO_FLAGS_H)
target_include_directories(basecpp PUBLIC
  include)
