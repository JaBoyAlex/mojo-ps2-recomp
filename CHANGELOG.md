# Changelog

## 1.0.0-rc.7

- Extend the 2D upscaler to paletted menu and HUD graphics, including the
  MOJO! corner logo, as well as the title splash and intro video.
- Rename the F1 option to **Upscale 2D** and the RecompLauncher option to
  **Upscale 2D artwork**. Existing preferences carry forward.

## 1.0.0-rc.6

- Reconstruct higher-resolution HUD texels from the player's local disc at
  runtime, keeping the original text and icon dimensions.
- Use the existing **Upscale HUD** setting in F1 and RecompLauncher. The
  portable release contains shader code and uses the same local setup on both paths.

## 1.0.0-rc.5

- Add **Upscale HUD** to F1 and RecompLauncher Game Settings. It refines edges
  on HUD text and icons at higher gameplay resolutions without changing their size.
- Keep existing HUD rendering as the default. Settings changes apply on restart.

## 1.0.0-rc.4

- Send CUE/BIN and CHD through the same exact disc validation as ISO in the
  RecompLauncher builder. Keep the serial check when the launcher can read it.
- Document the tested desktop installation from the public GitHub release.

## 1.0.0-rc.3

- Add an independent persistent right-stick Y toggle directly below X in F1.
- Preserve both left-stick axes; either camera axis can be reversed independently.
- Fix Windows subprocess selection of bundled Bash instead of the WSL stub.

## 1.0.0-rc.2

- Add a persistent F1 toggle for right-stick X inversion, applied immediately.
- Preserve right-stick Y, ball movement inputs and the neutral position.
- Exercise actual host controls, settings persistence and menu selection in CI.

## 1.0.0-rc.1

- Shared standalone and RecompLauncher local builder around the tested recompiler.
- Exact USA PS2 disc verification; ISO, BIN/CUE and single-track CHD import.
- Portable bootstrap, versioned local builds, separate saves and settings.
- Level 1–3 manifest, security gates and copyright-safe release packaging.
