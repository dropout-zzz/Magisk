#!/usr/bin/env bash

# this script is intended for uses in GitHub Actions.

set -e
cd native/src/external

exec git submodule update -j 4 --init --depth 1 --single-branch "$@" -- \
  corrosion \
  cxx-rs \
  nix-rs
