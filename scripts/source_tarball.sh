#!/usr/bin/env bash

set -e

sed 's/, "core", "init", "sepolicy"//' native/src/Cargo.toml > native/src/Cargo.toml.dropout

dot_hash="$(git rev-parse --short HEAD || true)"
dot_changes="$(git status --porcelain || true)"

if [ ${#dot_hash} -eq 7 ]; then
  dot_suffix+="-${dot_hash}"

  if [ ! -z "$dot_changes" ]; then
    dot_suffix+='-dirty'
  fi
else
  dot_suffix+='-dirty'
fi

dot_name="magiskboot-src${dot_suffix}"

rm -f "${dot_name}.txz"

export XZ_OPT='-9 -e -v -T1'

tar -c -f "${dot_name}.txz" -J -v --xform="s,^,${dot_name}/,S" \
  -X scripts/source_ignores.list \
  --exclude-vcs \
  --xform='s,\.dropout$,,' \
  CMakeLists.txt \
  build_magiskboot.sh \
  toolchain_android_armv8.cmake \
  docs/build_magiskboot.md \
  LICENSE \
  README.MD \
  native/src/CMakeLists.txt \
  native/src/Cargo.toml.dropout \
  native/src/Cargo.lock \
  native/src/base \
  native/src/boot \
  native/src/include \
  native/src/external/CMakeLists.txt \
  native/src/external/corrosion \
  native/src/external/cxx-rs \
  native/src/external/lz4 \
  native/src/external/nix-rs \
  native/src/external/lz4-sys \
  tools/keys/verity.pk8 \
  tools/keys/verity.x509.pem

echo
echo "created: ${dot_name}.txz"
echo
