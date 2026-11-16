# MOJO! Recomp v1.2.0-alpha.1 - native platform preview

**Experimental prerelease. Windows v1.1.0 remains the recommended stable release.**

Adds native Linux x86-64 and macOS Apple Silicon/Intel builders while retaining
the working ps2-native-recomp pipeline, renderer optimizations, camera options,
Upscale 2D, saves and settings. No Wine, Proton or PS2 emulator is required.
The release contains open-source helpers and source only; the game is generated
locally from the player's verified disc. No game executable or assets are shipped.

## Install

- Windows: extract the Windows x64 ZIP and open MOJO.exe.
- Linux: extract the Linux x64 tar.gz to a writable folder and run MOJO or
  Start-MOJO.sh. Install the native Clang and SDL development prerequisites
  listed in docs/PLATFORMS.md first. A working Vulkan driver is required.
- macOS: extract the matching arm64 or x64 ZIP and open MOJO.app. Requires
  macOS 15+ and Apple Command Line Tools. The app is ad-hoc signed, **not
  Developer ID signed or notarized**. Use normal macOS Open approval if needed;
  do not disable system protections.

All four packages use the same importer and builder. Supply your own MOJO! USA
PS2 SLUS_207.41 disc, SYSTEM.CNF VER 1.02, matching the exact ISO and executable
SHA-256 values in docs/COMPATIBILITY.md. Supported containers are ISO, CUE with
its matching BIN, and lossless single-track CD CHD. Other regions, revisions and
console versions are unsupported. Compilation and initial downloads take time;
Unix native toolchain installation is still a prerequisite.

Every package includes a schema-validated RecompLauncher Level 3 manifest:
headless preparation, progress, timeout/error handling, settings and saves.
Standalone installation works independently. RecompLauncher beta-channel
availability is controlled by its service; a GitHub prerelease does not
automatically enable a catalog beta. An extracted package can also be imported
locally. Ordinary players stay on the stable release.

## What was tested

- Native CI compiles and runs synthetic generated MIPS code on Linux x64,
  macOS ARM64 and macOS x64, including dynamic-library compilation/loading,
  VU tests, virtual controllers, saves, settings and GPU clear comparisons.
- Windows helper packaging and existing synthetic regression checks run in CI.
  Private Windows owner-disc boot regression preserves the v1.1.0 baseline.
- Private Linux standalone CUE/BIN preparation and Level 3 CHD preparation used
  the owner's SHA-256-matching disc. A 3,100-frame boot matched the Windows
  guest-cycle count. Linux RecompLauncher imported and launched the package
  and edited the same Upscale 2D setting as F1.
- The owner reached Stage 5 using keyboard input in a separate WSL2 GPU
  prototype. A corrected-clock session ran for about 7.5 minutes with no
  reported empty sound queues or dropped samples in the runtime diagnostics.

## Known limitations

- This is **not verified stable Linux or macOS gameplay support**. No Mac
  owner-disc gameplay test or regular Linux hardware playtest was available.
  CI startup is not equivalent to a full game playtest. Steam Deck and physical
  Unix controllers remain untested.
- WSL2 initially selected CPU Vulkan rendering. The isolated GPU test used an
  experimental, nonconformant Mesa Dozen bridge, which is neither shipped nor
  enabled in this release. WSL performance does not predict regular Linux
  performance.
- A real WSL host-clock mismatch was corrected for Linux host pacing without
  changing PS2 clocks or 60/50 Hz targets. The owner still noticed occasional
  visual cadence changes and audio crackling. An independent steady-tone SDL
  test reproduced uneven sound with MOJO! closed, establishing an audio-path
  problem outside the game. This does not rule out additional port issues;
  native hardware verification remains necessary.
- No new performance gain is claimed. The startup movie can stutter in WSL.
  The existing Windows stable release and its measured results remain separate.

Updates preserve player-owned data and keep prior locally generated builds.
Linux uses userdata beside the launcher; macOS uses
~/Library/Application Support/MOJO Recomp. Back up saves before experimental
testing. Never attach discs, generated game code, raw private logs or save files
to public issues. Report the OS/architecture, GPU backend, symptoms and whether
the issue also occurs in the stable Windows release.
