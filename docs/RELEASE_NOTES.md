# MOJO! Recomp v1.1.0 - Windows x64 portable builder

Make eligible full-page framebuffer/depth clears cheaper while preserving their
exact graphics-memory result. Other draws retain the existing renderer. Also
remove repeated division from power-of-two graphics and VU queue offsets;
ordering, synchronization, simulation timing and floating-point behavior remain
unchanged. Existing camera and 2D artwork options carry forward.

Three alternating-order comparisons against rc.7 on Windows 11, Core i5-11400,
RTX 3060 Ti, 32 GB RAM, D3D12, High resolution, Upscale 2D On:

| Measurement | rc.7 | v1.1.0 |
| --- | ---: | ---: |
| Normal-speed windowed FPS | 60.05 | 60.07 |
| Process CPU ms/frame in normal play | 7.008 | 6.755 |
| Uncapped single-threaded headless frames/s | 134.41 | 153.85 |
| Sampled GPU kernel ms/frame, headless profiling | 7.314 | 7.068 |

The uncapped headless test measured **14.5% higher throughput** on this PC.
Normal-play process CPU time/frame fell about **3.6%**. These are separate
measurements: headless throughput is not a normal gameplay FPS promise. Players
already at 60 FPS should expect approximately 0% additional FPS. There is no
supported percentage estimate for most PCs from this single host and scene.
Normal play keeps its limiter. See [methods and limitations](https://github.com/JaBoyAlex/mojo-ps2-recomp/blob/main/docs/PERFORMANCE.md).

Automated qualification:

- All 2,658 checkpoints matched across a 39,871-frame replay of an owner-recorded
  session on the multithreaded candidate.
- Boot replay: all 206 checkpoints and byte-identical audio matched in single-
  and multithreaded paths, for both upgraded and fresh standalone builds.
- All 32 compared movement-frame pairs matched rc.7 across four rendering scales
  with 2D upscaling off/on, independently for both builds.
- 96 synthetic whole-VRAM GPU comparisons matched; 433 native guard/parameter
  cases and 65,536 blend identities passed, along with queue and camera tests.
- Fresh standalone ISO setup and a RecompLauncher Level 3 headless CHD upgrade
  both built locally. Each installation passed a 3,100-frame standalone smoke
  test. Upgrade preserved all 16 protected files and the previous native runtime.
- The unchanged launcher manifest passed the official SDK schema. The final
  upgraded executable matched the regression-tested candidate after normalizing
  only link timestamps; the fresh build was checked functionally, not claimed
  byte-for-byte identical.

The owner completed the requested approximately five-minute normal-speed
playtest of this final candidate and reported no issues noticed. This is a
human report, separate from the automated checks.
This is the first stable release for the supported USA disc and documented
Windows configuration.

This portable ZIP contains a builder and licensed helpers, **not the game**.
Supply your own **MOJO! USA PS2 disc, SLUS_207.41, SYSTEM.CNF VER 1.02**, with
normalized ISO SHA-256
`bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5`.
ISO, CUE with its matching BIN, and lossless single-track CD CHD are accepted.
Other regions, Xbox copies and modified/unverified revisions are unsupported.

Extract `MOJO-Recomp-v1.1.0-Windows-x64.zip` into a writable folder and run
`MOJO.exe`, or install through RecompLauncher. Initial setup downloads verified
open-source tools and compiles using your disc; the game executable is never
shipped. Both installation paths use the same builder and preserve userdata.
Back up userdata before updating. No separate EXE installer is needed.

Windows 11/NVIDIA is the tested configuration. Broader hardware coverage, a
full game playthrough and real progression-save/restart qualification remain
open; see docs/COMPATIBILITY.md. The unreleased v1.0.0 work was held and folded
into this update; rc.7 remains the previous published version.
