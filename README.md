<h1 align="center">MOJO! PS2 Recomp</h1>

<p align="center">
  <strong>The PS2 puzzle game, running natively on PC.</strong><br>
  Bring your own verified USA disc. Play standalone or through RecompLauncher.
</p>

<p align="center">
  <a href="https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.1.0/MOJO-Recomp-v1.1.0-Windows-x64.zip"><img alt="Download the stable Windows x64 portable builder" src="https://img.shields.io/badge/Download-Windows_x64-287a48?style=for-the-badge" width="365" height="48"></a>
  &nbsp;
  <a href="https://recomplauncher.com/game/mojo-ps2-recomp"><picture><source media="(prefers-color-scheme: dark)" srcset="https://recomplauncher.com/assets/press/launcher/badge-light.svg"><img alt="Get it on RecompLauncher" src="https://recomplauncher.com/assets/press/launcher/badge-dark.svg" height="48"></picture></a>
</p>

<p align="center">
  <a href="#get-started">Get started</a> &nbsp;·&nbsp;
  <a href="#your-game-your-way">Features</a> &nbsp;·&nbsp;
  <a href="#required-game-copy">Required disc</a> &nbsp;·&nbsp;
  <a href="#documentation-and-credits">Documentation</a>
</p>

<p align="center">
  <a href="https://i.redd.it/gclcgts6u51i1.png"><img src="https://i.redd.it/gclcgts6u51i1.png" alt="Actual MOJO! native recomp gameplay: the red ball rolls toward a circular Stage 1 platform surrounded by space, with the original HUD visible." width="760"></a><br>
  <sub>Actual gameplay from the native recomp · Stage 1 · Click for the full-resolution image</sub>
</p>

## Your game, your way

| Native play | Picture options | Controls and comfort |
| --- | --- | --- |
| Build native PC code locally from your own verified disc using [ps2-native-recomp](https://github.com/exoteric33/ps2-native-recomp). | Native monitor resolution, fullscreen and optional **Upscale 2D** for HUD and menu artwork. | Controllers and keyboard, independent camera X/Y inversion, quick saves and an **F1** settings menu. |

The Windows build has been played beyond round 10 without reported bugs. This
is not a full-game compatibility guarantee; see the [tested status](docs/COMPATIBILITY.md).
The stable release also reduces framebuffer-clear and host-queue work, with
[measured results](docs/PERFORMANCE.md).

> **Bring your own game.** This project distributes the builder and open-source
> integration tools. No disc, BIOS, extracted assets, translated game code or
> prebuilt game executable is included.

## Get started

| Platform | Release | Download |
| --- | --- | --- |
| **Windows x64** | **v1.1.0 · Stable** | [Portable ZIP](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.1.0/MOJO-Recomp-v1.1.0-Windows-x64.zip) |
| Linux x64 | v1.2.0-alpha.2 · Experimental | [tar.gz](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.2.0-alpha.2/MOJO-Recomp-v1.2.0-alpha.2-Linux-x64.tar.gz) |
| macOS Apple Silicon | v1.2.0-alpha.2 · Experimental | [App ZIP](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.2.0-alpha.2/MOJO-Recomp-v1.2.0-alpha.2-macOS-arm64.zip) |
| macOS Intel | v1.2.0-alpha.2 · Experimental | [App ZIP](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.2.0-alpha.2/MOJO-Recomp-v1.2.0-alpha.2-macOS-x64.zip) |

**Windows v1.1.0 remains the recommended stable release.** Linux and macOS
packages have additional toolchain requirements and incomplete hardware/gameplay
validation. Read the [preview installation guide and known limitations](https://github.com/JaBoyAlex/mojo-ps2-recomp/blob/v1.2.0-alpha.2/docs/NATIVE_RELEASE_NOTES.md)
before trying them. The instructions below describe stable Windows setup.

### Play with RecompLauncher

1. Find **[MOJO! PS2 Recomp](https://recomplauncher.com/game/mojo-ps2-recomp)** in RecompLauncher and choose **Install**.
2. Choose **Play**, select your supported disc image and let setup build the game locally.
3. Choose **Play** on the Ready to Play screen. Resolution, fullscreen, camera
   inversion and Upscale 2D are also available in **Game Settings**.

The release includes **Level 3** integration: disc verification, headless setup,
progress reporting, settings and save backups. RecompLauncher is optional.

<details>
<summary>Alternative: add the project through its GitHub URL</summary>

In RecompLauncher's Library, choose **Add From GitHub or GitLab**, paste
`https://github.com/JaBoyAlex/mojo-ps2-recomp`, and add the project. Then follow
the Install and Play steps above. [Integration details](docs/RECOMPLAUNCHER.md)
and [executed validation](docs/VALIDATION.md).

</details>

### Play standalone

1. Extract the [Windows portable ZIP](https://github.com/JaBoyAlex/mojo-ps2-recomp/releases/download/v1.1.0/MOJO-Recomp-v1.1.0-Windows-x64.zip) into a writable folder.
2. Run **MOJO.exe** and choose your supported disc image. Keep CUE and BIN files together.
3. Allow setup to download verified build tools and compile your local game.
4. The game starts when setup finishes. Open **MOJO.exe** again for subsequent play.

First setup needs internet access, at least **5 GB free**, and several minutes.
It downloads about **300 MB** of open-source build tools, plus runtime dependencies.
No separate EXE installer or administrator access is required.

<details>
<summary>Windows requirements and source-checkout setup</summary>

Windows 10/11 x64 is the intended platform. Windows 11 with an NVIDIA RTX 3060 Ti
is the tested environment. A working **Direct3D 12** GPU driver is required.
The archive is a local builder; its compiler remains available for translating
previously unseen code during play.

From this stable source checkout, use
`Start-MOJO.cmd -Game "D:\Games\Mojo.iso"`, or first
[build the file-picker executable](docs/BUILDING.md). Source and release paths
use the same Python builder and upstream pipeline. To inspect the experimental
Unix source, use the [v1.2.0-alpha.2 tag](https://github.com/JaBoyAlex/mojo-ps2-recomp/tree/v1.2.0-alpha.2).

</details>

## Required game copy

Only **MOJO! USA for PlayStation 2**, serial **SLUS_207.41**, with
**SYSTEM.CNF VER 1.02** and the [verified SHA-256 hashes](docs/COMPATIBILITY.md),
is supported. VER is the observed disc metadata, not an invented retail revision name.

Accepted images: **ISO**, **CUE with its matching BIN**, or a **lossless CHD of
the supported single-track CD**. The builder verifies the complete normalized
ISO and original boot executable before translating anything. A filename alone
never establishes compatibility.

European, Japanese, Xbox, modified and other unverified copies are unsupported.
Supply your own legally obtained image; no source for commercial game data is provided.

## Controls and settings

| Shortcut | Action |
| --- | --- |
| **F1** | Open settings and view control bindings |
| **F11** | Toggle fullscreen |
| **F5 / F8** | Quick-save / quick-load |

SDL2 controllers and keyboard are supported; the tested controller was an
**8BitDo Ultimate 2C**. RecompLauncher Big Picture starts fullscreen.

- **Upscale 2D:** clearer HUD, menus and startup artwork at their original size.
  Use **Enhanced** rendering resolution or higher, enable it in F1 or
  RecompLauncher, then restart. It defaults to Off and reconstructs artwork
  locally from your own disc.
- **Camera inversion:** **Invert right stick X** and **Invert right stick Y**
  are independent and take effect immediately. Both default to Off, preserving
  the original behavior. Neither affects left-stick movement; explicitly mapped
  keyboard or mouse right-stick inputs follow the same setting.

## Saves and updates

On Windows and Linux, your local game, disc copy, settings and saves live in
`userdata/`. The memory card is `userdata/saves/mojo.ps2`; artwork and camera
preferences use `userdata/saves/keys.ini`. **Back up this folder and do not share it.**
The macOS preview keeps its data in `~/Library/Application Support/MOJO Recomp`.

Extract an update over the same installation. Releases contain no player data,
and new native builds use separate versioned folders, becoming active only after
a successful build. Keep older builds while they are running. RecompLauncher
backs up the memory card and settings; quick states and compiler caches are excluded.

## Documentation and credits

[Build from source](docs/BUILDING.md) · [Architecture](docs/ARCHITECTURE.md) ·
[Troubleshooting](docs/TROUBLESHOOTING.md) · [Compatibility](docs/COMPATIBILITY.md) ·
[Source provenance](docs/SOURCES.md) · [Security](SECURITY.md) · [Legal scope](docs/LEGAL.md)

Built on [ps2-native-recomp](https://github.com/exoteric33/ps2-native-recomp)
by exoteric33 and contributors. Credit for MOJO! belongs to its original creators
and rights holders. The gameplay image is from the project's
[public showcase](https://www.reddit.com/r/recomps/comments/1xu9kro/mojo_ps2_now_runs_natively_on_windows/).
This unofficial project is not affiliated with or endorsed by the original publisher or Sony.
