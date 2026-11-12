# MOJO! PS2 Recomp

A local Windows builder for the USA PlayStation 2 version of **MOJO!**. It uses
[ps2-native-recomp](https://github.com/exoteric33/ps2-native-recomp) to translate
your own verified disc into native PC code. No game files, translated game code,
BIOS, or prebuilt game executable are distributed.

**Release candidate.** The original working build has been played beyond round
10 without reported bugs. This is not a claim of complete game compatibility.
See [test status and limitations](docs/COMPATIBILITY.md).

Download the portable builder from this project's
[GitHub Releases](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases).

<a href="https://recomplauncher.com"><picture><source media="(prefers-color-scheme: dark)" srcset="https://recomplauncher.com/assets/press/launcher/badge-light.svg"><img alt="Get it on RecompLauncher" src="https://recomplauncher.com/assets/press/launcher/badge-dark.svg" height="48"></picture></a>

## Required game copy

Only **MOJO! USA, PS2 serial SLUS_207.41, SYSTEM.CNF VER 1.02**, matching the
[verified hashes](docs/COMPATIBILITY.md), is supported. The VER field is copied
from the disc metadata; it is not an invented retail revision name. European,
Japanese, Xbox, modified and other unverified copies are not supported.

Supply your own legally obtained disc image: ISO, BIN/CUE, or a lossless CHD of
the supported single-track CD. A filename alone never establishes compatibility.
The builder verifies the normalized ISO and original boot executable SHA-256
before translating anything. No download source for commercial game data is provided.

## Standalone installation

1. Extract `MOJO-Recomp-v1.0.0-rc.1-Windows-x64.zip` into a writable folder.
2. Run `MOJO.exe` and choose your disc image. For BIN/CUE, keep the two files together.
3. Let setup download checksum-pinned open-source build tools (about 300 MB,
   plus runtime dependencies). Allow at least 5 GB free and several minutes.
4. The game starts when compilation finishes. Run `MOJO.exe` again to play.

Windows 10/11 x64 is the intended platform; Windows 11 on an NVIDIA RTX 3060 Ti
is the tested environment. A working D3D12 GPU driver and internet access for
first setup are required. Setup does not need administrator rights. The portable
archive is a builder, not an installer; the compiler remains local for runtime
translation of previously unseen code. RecompLauncher is optional.

From a source checkout, use `Start-MOJO.cmd -Game "D:\Games\Mojo.iso"`, or first
[build the file-picker executable](docs/BUILDING.md). Source and release paths
use exactly the same Python builder and upstream pipeline.

## RecompLauncher installation

The release root includes `recomplauncher.json`. With a verified developer account,
in RecompLauncher's developer settings, enable local builds, add the extracted release folder, run **Check**,
then **Setup** and choose the supported disc. Setup invokes `MOJO.exe --prepare
--game <image>` with progress reporting and a two-hour limit. **Play** invokes
the same executable and local build. Catalog listing requires separate submission;
the badge alone does not mean this project is listed. The Level 3 protocol is
tested; full desktop Setup/Play remains unverified because the test account does
not expose Developer tools. Do not treat this as completed desktop certification.

The settings screen offers Native monitor resolution and rendering options with
pixel dimensions. Fullscreen uses the desktop display mode and preserves the
game aspect ratio; internal rendering resolution is separate. Big Picture mode
starts fullscreen. [Integration details](docs/RECOMPLAUNCHER.md).

## Controls, saves and updates

SDL2 controllers and keyboard are supported. The tested controller was an
8BitDo Ultimate 2C. F1 opens the runtime menu; F11 toggles fullscreen;
F5/F8 quick-save/quick-load. The menu shows control bindings.

All locally generated game files, the disc copy, settings and saves are under
`userdata/`. The memory card is `userdata/saves/mojo.ps2`. Do not share this
folder. Back it up before updates. Extract a newer release over the same install;
release archives never include `userdata/`. New native builds use separate
versioned folders and the active pointer changes only after a successful build.
Do not delete older builds while they are running. RecompLauncher backs up the
memory card and settings; quick states and compiler caches are intentionally excluded.

## Development and credits

See [building](docs/BUILDING.md), [architecture](docs/ARCHITECTURE.md),
[troubleshooting](docs/TROUBLESHOOTING.md), [source provenance](docs/SOURCES.md),
[legal scope](docs/LEGAL.md), and [security](SECURITY.md).

Credit belongs to the original MOJO! creators and rights holders for the game,
and to exoteric33 and contributors for ps2-native-recomp. This unofficial project
is not affiliated with or endorsed by the original publisher or Sony.
