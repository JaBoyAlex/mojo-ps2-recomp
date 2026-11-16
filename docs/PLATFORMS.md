# Native platform development

The Windows v1.1.0 release remains the gameplay compatibility baseline. Native
Linux x86-64 and macOS ARM64/x86-64 packages are under validation. Native CI
compilation is not a claim of MOJO! gameplay compatibility.

## Architecture

Retain MIT-licensed ps2-native-recomp at the existing pinned commit. Its SDL2,
wgpu Vulkan/Metal backends, portable Clang vectors, POSIX subprocesses and dynamic
library compiler already cover the required architecture. MOJO!'s validated
runtime patches remain shared. Unix additionally supports stock macOS Bash 3.2
and disables floating-point contraction explicitly, including on ARM64.

Alternatives reviewed: [PS2Recomp](https://github.com/ran-j/PS2Recomp) describes
an experimental analyzer/runtime and x86 SIMD requirements; it provides no
verified MOJO! migration advantage. [Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp)
is a game-specific port, not a drop-in MOJO! runtime. [ps-recomp](https://github.com/plaught-armor/ps-recomp)
uses Odin and describes macOS as untested. None justifies replacing the working
framework, rendering behavior or regression fixtures. No code was copied from
these alternatives.

## Installation

Windows: use the existing portable ZIP and MOJO.exe. Setup is unchanged.

Linux preview: extract the native package to a writable folder; run Start-MOJO.sh
or MOJO. GTK3 provides the disc picker. Without GTK3, pass `--game /path/to/disc.cue`.
Bash, curl, Clang with C++20 `<format>`, and native SDL2 development
prerequisites are required. On Ubuntu 24.04: install clang-19,
libc++-19-dev, libc++abi-19-dev, libx11-dev, libxext-dev, libxrandr-dev,
libxcursor-dev, libxi-dev, libxfixes-dev, libasound2-dev, libpulse-dev and libudev-dev.
A working Vulkan driver is required. Steam Deck packaging is not yet verified.
No Wine or Proton is used.

macOS preview: extract the matching architecture ZIP and open MOJO.app. macOS 15+
and Apple Command Line Tools are required (`xcode-select --install`). The Cocoa
picker and preparation progress window use the same headless builder. The bundle
is ad-hoc signed during packaging for integrity; it is **not Developer ID signed
or notarized**. Gatekeeper may require the normal system Open approval. Do not
disable Gatekeeper or system integrity protection. Game compilation uses Clang
and ordinary local dynamic libraries, without hardened-runtime restrictions or
unrestricted JIT entitlements. Real hardware verification remains required.

The bootstrap downloads a pinned native Python 3.13.18 distribution and
SHA-256-checked CMake/Ninja wheels, framework
source and SDL2 source, and compiles SDL2 locally. The framework downloads its
own pinned/hash-checked wgpu-native dependency. The compiler remains available
for unseen EE/VU code. Native toolchain prerequisite installation is still a
manual step on Unix; this preview does not claim a dependency-free first start.

All platforms require exactly the supported USA PS2 SLUS_207.41 revision
(SYSTEM.CNF VER 1.02) documented in COMPATIBILITY.md. ISO, CUE/BIN and bounded
single-track CHD use the same importer and exact ISO/ELF SHA-256 checks.

## RecompLauncher

Both Level 3 preparation and Play call the same executable and builder as
standalone setup. Every platform archive has its own root recomplauncher.json.
The current official schema allows program fallback lists, but no OS-specific
prepare override; packaging selects appropriate executable paths instead.
Settings, Big Picture fullscreen, exit codes and 7200-second timeout are retained.
Known dump sizes/CRCs come from the SHA-256-matching project reference documented
in COMPATIBILITY.md; they are not claimed as independently certified Redump data.
The builder still enforces exact SHA-256 verification, independently of the badge.

Linux data stays in userdata beside MOJO. macOS data is stored in
`~/Library/Application Support/MOJO Recomp`, outside the signed/read-only app.
The macOS manifest points settings and save backups there too. Updates contain
no player settings, saves, discs, generated runtimes or build caches. Build
indices include the host architecture, avoiding reuse of incompatible binaries.

## Validation boundary

Native CI runs separate Linux, Apple Silicon and Intel Mac runners. It compiles
native helpers and the patched runtime, generates code from independently
authored synthetic MIPS instructions, starts it, tests virtual controllers,
saves, damaged disc rejection, VU operations, queue ordering, fast clear guards,
live dynamic-library compilation/loading and incremental rebuilds. These tests
must succeed before artifacts are accepted. No commercial fixtures or private
gameplay files are uploaded to CI. Physical controllers, real audio output,
visible Vulkan/Metal rendering, MOJO! disc preparation and gameplay still need
native-system testing. GPU results are not assumed bit-identical across APIs.

No new performance improvement is claimed. Windows engine, timing and gameplay
patches remain pinned; its normal regression suite remains required.

Remaining improvements: automatic portable Unix compiler/dependency acquisition
(medium), broader distribution/Steam Deck testing (medium), Developer ID signing
and notarization (requires credentials), controller-only setup/quit (medium),
and Recomp Achievements (large). The existing RecompLauncher listing and badge
remain in place; no resubmission is required merely to ship a manifest.
