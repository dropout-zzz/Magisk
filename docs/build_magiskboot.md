# Building MagiskBoot

This [fork](https://en.wikipedia.org/wiki/Fork_(software_development)) has added supports for running the [MagiskBoot](https://topjohnwu.github.io/Magisk/tools.html#magiskboot) utility program on some additional OSes:
- Windows 11 (via [Cygwin](https://www.cygwin.com/) environment. [MSVC](https://learn.microsoft.com/en-us/cpp/overview/visual-cpp-in-visual-studio?view=msvc-180) and [MinGW](https://www.mingw-w64.org/) are not supported. [MSYS2](https://www.msys2.org/) should not be used.)
- macOS 12 or newer

But building for these platforms are also supported using the instructions provided in this documentation:
- [GNU/Linux](https://en.wikipedia.org/wiki/GNU/Linux)
- Android

This documentation describes how to work with source code of MagiskBoot and how to [compile](https://en.wikipedia.org/wiki/Compiler) the program from [source code](https://en.wikipedia.org/wiki/Source_code), so you can use the program on your computer.

> [!IMPORTANT]
> This is just a fork, so please, DON'T report problems with MagiskBoot you got from this repository to the original [Magisk](https://github.com/topjohnwu/Magisk) project!

## Setup Environment

> [!NOTE]
> This part assumes you install everything from your [distribution](https://en.wikipedia.org/wiki/System_distribution)'s [package manager](https://en.wikipedia.org/wiki/Package_manager).

- On macOS: You will need a package manager, which you may pick from [Homebrew](https://brew.sh/) or [MacPorts](https://www.macports.org/). If you have an old version of macOS, MacPorts might work better. You may use "AppleClang" C++ compiler that comes with [Xcode](https://developer.apple.com/xcode/) or a C++ compiler installed through package manager if it doesn't work.
- On Cygwin: Install packages using the [setup.exe](https://www.cygwin.com/install.html) program that you downloaded from Cygwin site. Make sure you select `gcc-core` version 15.x or newer. Ensure to install the Rust compiler using the `setup.exe` program and not through [rustup](https://rustup.rs/). Ensure that `cygwin-devel` package is installed if it's not the case.
- Alpine Linux based distributions only: Ensure `linux-headers` and `musl-dev` is installed through the [apk](https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper) command.
- Install [CMake](https://cmake.org/) 4.2.0 or higher.
- Install [GNU Make](https://www.gnu.org/software/make/manual/html_node/index.html) if it wasn't installed automatically with CMake.
- Non-Android only: Install [LZ4](https://lz4.org/) compression library with development files ([headers](https://en.wikipedia.org/wiki/Header_file)), this sometimes has the `-dev`, `-devel` or similar suffix in the package name.
- Install [Rust](https://rust-lang.org/) compiler 1.91.1 or newer and the [Cargo](https://doc.rust-lang.org/cargo/) program.
- Ensure that you have [GCC](https://gcc.gnu.org/) version 15.x or newer, or a new enough [Clang](https://clang.llvm.org/)'s [C++](https://en.wikipedia.org/wiki/C%2B%2B) compiler.
- Android only: Install [NDK](https://developer.android.com/ndk), which comes with a Clang compiler suitable for Android. Ensure `ANDROID_NDK_ROOT` or `ANDROID_NDK` [environment variable](https://en.wikipedia.org/wiki/Environment_variable) is set to point to installation path of NDK (which contains the "toolchains" directory).
- Install [Git](https://git-scm.com/), then clone this repository: `git clone https://github.com/dropout-zzz/Magisk --depth=1 --single-branch --no-tags --recursive --shallow-submodules`. Alternatively (recommended if you don't plan to do development), download a source code tarball from [GitHub Releases](https://github.com/dropout-zzz/Magisk/releases) (file named `magiskboot-src-X.txz`) which is smaller and easier, then extract the archive using [tar](https://en.wikipedia.org/wiki/Tar_(computing)) command: `tar xvf ARCHIVE` (replace `ARCHIVE` with the file name; make sure you have [XZ](https://tukaani.org/xz/) installed).

## Building

- To build the MagiskBoot program, run the configuration with CMake: `cmake -S . -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PWD` (you need to be inside the cloned repository, use something like a `cd path/to/repo` command), then start the build process: `./build_magiskboot.sh .` . Once the build is complete, run `cmake --install . --strip` and the output will be located under `bin` directory.
- In order to build for Android, use the `--toolchain toolchain_android_armv8.cmake` option when you run the CMake configuration command and change the [architecture](https://en.wikipedia.org/wiki/Comparison_of_instruction_set_architectures) string [accordingly](https://cmake.org/cmake/help/latest/variable/CMAKE_ANDROID_ARCH_ABI.html) in the toolchain file.
- Sometimes you need to use a different compiler (for example, if the default one that CMake picks up is too old to successfully build MagiskBoot), you can do this by setting `CXX` environment variable to the path or name of the C++ compiler you wanted to use (for example: `export CXX="/opt/local/bin/g++-mp-15"`), before running CMake configuration command.
- [Cross-compilation](https://en.wikipedia.org/wiki/Cross_compiler), Linux only: Sometimes you may need to set `Rust_CARGO_TARGET` CMake variable manually, please refer to the [Corrosion documentation](https://corrosion-rs.github.io/corrosion/usage.html#linux-to-linux).
- To test if your compiled MagiskBoot is working, you can install [Python](https://www.python.org/) and run this script: `./scripts/test_magiskboot.py bin/magiskboot`. To run this test on Android, you can copy the MagiskBoot you got into your phone and do it in [Termux](https://termux.dev/). If the test passes, you should see a message saying: "all tests succeeded.".

## IDE Support

- To develop the C++ portions of MagiskBoot code, use the `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` option when you run the CMake configuration command, then use a code editor with [Clangd](https://clangd.llvm.org/) support (for example, [KDE Kate](https://kate-editor.org/)).
- For Rust portions, use an editor with [rust-analyzer](https://rust-analyzer.github.io/) support.
- You should do a successful build first before you open source files in the editor.
