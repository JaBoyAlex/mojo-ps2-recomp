# Sources actually used

| Component | Source / pinned version | Role / license |
| --- | --- | --- |
| ps2-native-recomp | https://github.com/exoteric33/ps2-native-recomp/tree/57ef1197c0b818b9a4e1dbb98b1588da38586ffb | Importer, translator, native runtime, portable toolchain scripts; MIT |
| libchdr | https://github.com/rtissera/libchdr/tree/93d8c239ff0d4e8d7722985992649fce12d2463b | CHD decompression; BSD-3-Clause and bundled dependency notices |
| LLVM/llvm-mingw | https://github.com/mstorsjo/llvm-mingw/releases/tag/20260908 | Local compiler; upstream licenses retained by downloads |
| SDL2 | https://github.com/libsdl-org/SDL/releases/tag/release-2.32.10 | Input, window, audio; zlib |
| wgpu-native | https://github.com/gfx-rs/wgpu-native/releases/tag/v29.0.1.1 | Graphics; MIT/Apache-2.0 |
| DirectXShaderCompiler | https://github.com/microsoft/DirectXShaderCompiler/releases/tag/v1.9.2609 | D3D12 shaders; upstream LLVM/MIT notices |
| AMD FidelityFX FSR 1 | https://github.com/GPUOpen-Effects/FidelityFX-FSR/blob/a21ffb8f6c13233ba336352bdff293894c706575/ffx-fsr/ffx_fsr1.h | EASU kernel adapted to WGSL for transparent HUD textures; MIT |
| RecompLauncher SDK | https://recomplauncher.com/sdk-files/recomplauncher-agent.md | Manifest/protocol reference, retrieved 2026-11-11 |
| Gitleaks | https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 | Development/release secret scanning; MIT, not bundled |

The pinned upstream portable script additionally downloads CMake 4.4.4, Ninja
1.13.2, Python 3.13.16, MinGit 2.56.0.2 and BusyBox for Windows, verifying its
embedded SHA-256 values. These are downloaded tools, not game dependencies copied
into this source repository. Upstream runtime dependency scripts verify downloads.

CHD test fixture creation used chdman 0.287 obtained from the namDHC v2.0 tools
release (https://github.com/umageddon/namDHC/releases/tag/v2.0), verified SHA-256
`e475e5422e17557f38ec8e430e001cf566f377fed353d43c33a9fd8ce70c729d`.
It is not redistributed or required by end users. No game test fixture is published.
