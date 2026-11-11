# Architecture

The original working framework is retained at commit
`57ef1197c0b818b9a4e1dbb98b1588da38586ffb`. Its portable toolchain, disc importer,
EE/VU translators, native runtime and `port.sh` build orchestration are reused.
The publication project wraps them; it does not implement a second recompiler.

The main PS2 ELF is MIPS R5900 code. The framework translates EE blocks into C++
and compiles a native Windows executable. Exploration records VU programs for
translation. IOP code remains interpreted with high-level kernel/services, and
unseen EE/VU blocks may use live compilation or interpretation. This is a hybrid
native recompilation runtime, not a claim that every PS2 component is fully static.
No external PS2 BIOS is required. Graphics use wgpu compute rasterization over
D3D12; SDL2 provides windows, input and audio. No game-specific patches were
needed for the known-good game. A small host-menu text patch adds explicit gameplay
render dimensions and queries SDL's current desktop mode for the Native display
label. It changes no renderer behavior, game logic or save format.

`MOJO.exe` is only an independently authored bootstrap. PowerShell downloads
hash-pinned source/tools and invokes `builder/build.py`. That shared builder
normalizes the image using upstream `disc.py` (libchdr for CHD), verifies the full
ISO and boot executable, invokes upstream `port.sh`, then installs a versioned
local runtime. A Windows lock prevents simultaneous builds/game sessions in one
installation; a process job terminates children when setup is cancelled.

The native game executable contains translated commercial game code. It, the
original ELF, generated C++, disc data, caches, memory cards and states remain
local and must never be committed, uploaded as artifacts, or released.
Only bootstrap/helper binaries are distributable in the portable release.
