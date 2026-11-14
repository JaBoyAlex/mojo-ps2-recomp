# Validation record

v1.1.0 automated qualification (2026-11-14):

- 39,871-frame owner-recorded session replayed on the multithreaded candidate;
  all 2,658 checkpoints matched.
- Both the upgraded build and a fresh standalone build matched all 206 boot
  replay checkpoints and audio bytes in single- and multithreaded runs. Each
  also matched 32 movement-frame pairs across scales 1-4 and Upscale 2D off/on.
- The native clear guard passed 433 cases and 65,536 blend identities. The GPU
  fixture matched full randomized graphics memory in all 96 cases. Six
  multithreaded stress runs passed without the unsafe timing-diagnostic mix.
- Fresh standalone ISO preparation downloaded fresh pinned engine source and
  reused only open-source tool downloads. It built successfully and passed a
  3,100-frame standalone smoke. This was not a clean VM or a tool-download test.
- The SDK Level 3 prepare command upgraded the isolated installation from a
  verified CHD, emitting progress through completion. All 16 protected files
  matched their original hashes, including saves, settings, disc and recordings;
  the previous runtime remained available. A subsequent standalone 3,100-frame
  smoke also passed without changing those files.
- The upgraded runtime matched the regression candidate after normalizing only
  PE link timestamps. Runtime/host/generated source matched in the fresh build;
  its different binary bytes were qualified by replay, audio and frame tests.
- Final installed-build performance comparisons are in PERFORMANCE.md. The
  official RecompLauncher schema and all seven Python synthetic tests passed.
- The owner completed the requested approximately five-minute normal-speed
  playtest of the final candidate and reported no issues noticed. This human
  report is separate from the automated results.

Earlier queue-only candidate (unreleased v1.0.0 work): owner completed the requested approximately
five-minute normal-speed playtest and reported no issues noticed. This is a
human report, separate from automated results.

Queue-offset optimization: see [the performance report](PERFORMANCE.md) for the
research, measured comparisons, exact regression scope and limitations. The
release uses the same standalone and RecompLauncher prepare pipeline.

2D artwork upscaling (1.0.0-rc.7):

- Compared matched Ultra frames from both studio intros and the MOJO! title
  splash. Each used higher-resolution texture samples with Upscale 2D enabled.
- Compared three main-menu frames from the same saved state. The corner logo,
  mode label and arrows changed with the expanded filter. Pixels outside those
  UI regions matched. With the option Off, the full frames matched rc.6.
- Compared four Stage 1 motion frames at each rendering resolution. Original
  resolution was identical with the option On and Off. At Enhanced, High and
  Ultra, the changed pixels stayed within the HUD regions.
- Replayed 3100 frames with Upscale 2D enabled. All 206 checkpoints matched.
  A scripted controller toggled the option in F1 and verified it after restart.
- Prepared rc.7 over an isolated rc.6 installation. Disc, settings and memory
  card hashes matched after the upgrade. The updated manifest passed SDK schema
  validation, and the standalone launcher opened rc.7 with the option enabled.

HUD texture reconstruction (1.0.0-rc.6):

- Built over an isolated rc.5 installation using the manifest's headless
  prepare command and a verified CHD. SHA-256 checks matched the original
  local disc, memory card, controls and display settings after the upgrade.
- The packaged launcher accepted the verified CUE/BIN through the same
  prepare command and reused the local build. The standalone launcher then
  reached 3100 frames and exited successfully without a disc argument.
- Captured four matched Stage 1 gameplay frames at each of the four rendering
  resolutions on Windows 11 and Direct3D 12. Off matched rc.5 Off exactly.
  At Enhanced, High and Ultra the changes were confined to the HUD regions.
  At Original resolution the On and Off frames were identical.
- Compared the same Ultra frame with Upscale HUD On in both releases. The
  reconstructed timer and stage label had smoother curved and diagonal
  outlines at the same size. This is a visual check of the sampled HUD, not
  a full-game review of every texture.
- A virtual controller toggled Upscale HUD in F1 and the setting took effect
  after restart. All 206 checkpoints matched across a 3100-frame replay.
- The updated RecompLauncher manifest passed JSON schema validation.

HUD upscaling (1.0.0-rc.5):

- Compared four matched Stage 1 gameplay frames on Windows 11 with Direct3D 12
  at each rendering resolution. At Enhanced, High and Ultra, enabling the
  filter changed the sampled HUD pixels while the pixels outside the HUD areas
  stayed identical. Output dimensions matched at each setting. Original
  resolution was pixel-identical with the option on and off.
- At High resolution, the default output for the sampled gameplay frame matched
  rc.4 exactly. All 206 replay checkpoints matched across 3100 frames.
- A scripted virtual controller selected **Upscale HUD** in the F1 menu. It
  preserved the camera and resolution settings and applied the filter after
  restarting the native runtime.
- RecompLauncher beta 37 displayed the candidate manifest's setting as Off by
  default. Choosing On wrote the same INI key that F1 uses and preserved the
  other settings. This check used the existing desktop test install.
- The portable rc.5 package prepared a new build over an isolated rc.4 install.
  The original disc, memory card, controls and settings file hashes matched.

Desktop RecompLauncher beta 37 on Windows 11:

- Added the public GitHub project through **Add From GitHub or GitLab**. The
  launcher downloaded rc.3, opened its own setup screen from Play, accepted the
  verified ISO, downloaded a fresh toolchain, and built the game with visible
  progress. Ready to Play led to the native MOJO! main menu.
- Game Settings showed Display, Rendering resolution, and the separate
  right-stick X and Y controls.
- The rc.3 manifest rejected CHD during launcher preflight. With the rc.4
  manifest in the same isolated install, selecting the original CUE picked up
  its BIN, validated the exact normalized ISO hash, and launched the native
  runtime. This exercised the existing builder with the corrected manifest.

Camera update (1.0.0-rc.3): all four independent toggle combinations passed in
the native SDL virtual-controller test, each exiting zero after 150 frames:

| X invert | Y invert | Left X/Y | Right X/Y |
| --- | --- | --- | --- |
| Off | Off | 160 / 96 | 64 / 192 |
| On | Off | 160 / 96 | 191 / 192 |
| Off | On | 160 / 96 | 64 / 63 |
| On | On | 160 / 96 | 191 / 63 |

Compiled host tests passed all four settings round-trips and verified that the Y
menu item immediately follows X. The original game inverts both camera axes, as
confirmed by the user's comparison with the first build. Neither toggle changes
left-stick movement. The failed rc.2 CI run did not publish a release: it exposed
Windows selecting the WSL Bash stub, corrected with explicit PATH resolution.

Camera update (1.0.0-rc.2): the actual native SDL input path was exercised with a
scripted virtual controller in two runs. With inversion off, left X/Y were 160/96
and right X/Y were 64/192. With inversion on, only right X changed, to 191; right Y
remained 192 and left X/Y remained 160/96. Both runs exited zero after 150 frames.
Compiled host tests passed neutral/endpoints, disabled behavior, settings
round-trip, preservation of unrelated settings, and the F1 menu toggle command.

This file records executed checks only. No raw logs, screenshots or
commercial fixtures belong in the source repository.

- Standalone fresh toolchain download, verified BIN/CUE import, native compilation:
  passed on the existing Windows 11 test host.
- Standalone headless launch: passed, runtime reached 3100 frames and exited zero.
- CHD reader: passed, CHD made from the supported BIN/CUE decoded to the exact
  verified ISO SHA-256. This test used libchdr 0.3.0 and a locally generated CHD.
- Manifest: passed the official JSON schema retrieved 2026-11-11.
- RecompLauncher Level 3 protocol: the manifest's prepare command passed in a
  separately extracted release under a path containing spaces and a non-ASCII
  character, with RECOMPLAUNCHER=1. It downloaded a fresh toolchain, imported CHD,
  built the game, and subsequently completed a 3100-frame headless launch.
- Progress lines increased monotonically to 1.0. Invalid synthetic ISO and CHD
  inputs were rejected with exit code 20.
- Upgrade: overlaid the release onto a real prior local build marked as an older
  builder version, rebuilt, and verified unchanged SHA-256 for the disc, memory
  card, settings and binding file. The prior runtime remained present. This was
  a simulated older-version fixture, not a previously published release.
- Regression after the menu-label patch: all 206 existing replay checkpoints
  matched across 3100 frames against the known-good recording, independently for
  both the standalone build and the CHD/RecompLauncher-protocol build.
- Source-checkout command wrapper (`Start-MOJO.cmd -Prepare -Game <ISO>`) passed
  independently of RecompLauncher.
- Seven synthetic unit/security-gate tests passed. The menu-only rendering was
  visually checked at 960x720 with sample desktop dimensions: labels fit without
  clipping. This is not a live monitor-switching test.
- The original upstream checkout remains unmodified; the working game backup is
  kept outside the publication repository.
- Publication security: Gitleaks 8.30.1 passed the allowlisted source, staged
  content, complete reachable Git history and extracted release archive. The
  independent gate passed source, staged blobs, all reachable commit trees,
  archive membership and helper binary strings. No game material or private
  information was found in the audited publication set. The six public LLVM
  CI-path exceptions are documented in SECURITY.md; no secret rules were suppressed.
- License notices cover the helper libraries and compiler runtime. No game
  redistribution rights are asserted. No LFS objects or submodules are used.
- Original user playtest beyond round 10 remains evidence for the preserved
  engine/game pipeline, not a complete qualification of every packaging path.

The Developer tab's **Check** action was unavailable to the test account.
The Setup and Play tests above used the normal desktop Library.

The public repository is https://github.com/JaBoyAlex/mojo-ps2-recomp.
The first Windows GitHub Actions run passed unit tests, official SDK schema
validation, a fresh helper build, source/history/archive security checks, and
artifact upload: https://github.com/JaBoyAlex/mojo-ps2-recomp/actions/runs/43111409909.
No commercial game files were supplied to CI. GitHub's own secret-scanning API
reported that the feature is unavailable for this private repository; local and
CI Gitleaks plus the independent publication gate remain enforced.

A pristine Windows VM game installation, real game progression save/load, a full game playthrough,
and interactive resolution-menu qualification remain uncompleted. Dependency
downloads and builds were fresh on the existing host, not a clean-machine claim.
