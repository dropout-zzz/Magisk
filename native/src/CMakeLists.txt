add_subdirectory(external)

corrosion_import_crate(
  MANIFEST_PATH Cargo.toml
  CRATES magiskboot
)

# allow us to build with stable Rust.
corrosion_set_env_vars(magiskboot RUSTC_BOOTSTRAP=base,magiskboot)

add_subdirectory(base)
add_subdirectory(boot)
