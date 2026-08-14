#!/bin/bash

set -e

[[ $# -lt 1 || -z "$1" || ! -d "$1" ]] && {
  echo "usage: $0 <build directory> [arguments...]" >&2
  exit 1
}

dot_builddir="$1"
shift 1

# build Rust components first, this generates
#  files that needed by the C++ components.
cmake --build "$dot_builddir" -t cargo-build_magiskboot "$@"

cmake --build "$dot_builddir" "$@"
