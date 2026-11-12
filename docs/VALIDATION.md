# Validation record

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

This file records executed checks only, on 2026-11-11. No raw logs, screenshots or
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

RecompLauncher beta 37 was installed from its official signed download and opened.
Its Developers tab was unavailable to the current account. Source inspection
confirmed its verified-developer gate. Full desktop Check/Setup/Play testing is
therefore incomplete; protocol success is not substituted for that UI test.

Private GitHub publication is complete at https://github.com/JaBoyAlex/mojo-ps2-recomp.
The first Windows GitHub Actions run passed unit tests, official SDK schema
validation, a fresh helper build, source/history/archive security checks, and
artifact upload: https://github.com/JaBoyAlex/mojo-ps2-recomp/actions/runs/43111409909.
No commercial game files were supplied to CI. GitHub's own secret-scanning API
reported that the feature is unavailable for this private repository; local and
CI Gitleaks plus the independent publication gate remain enforced.

A pristine Windows VM game installation, real game progression save/load, a full game playthrough,
and interactive resolution-menu qualification remain uncompleted. Dependency
downloads and builds were fresh on the existing host, not a clean-machine claim.
