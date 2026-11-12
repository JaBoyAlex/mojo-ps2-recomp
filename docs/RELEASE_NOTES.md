# MOJO! Recomp 1.0.0-rc.2 — Windows x64 portable builder

Adds **F1 → Invert right stick X**. It changes horizontal camera input only,
applies immediately, and persists across restarts. Right-stick Y and ball movement
remain unchanged. Off preserves the game's original controls.

This archive contains a builder and open-source helper tools, not the game.
Supply your own **MOJO! USA PlayStation 2 disc, SLUS_207.41, SYSTEM.CNF VER 1.02**.
Only the exact normalized ISO SHA-256
`bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5`
is supported. ISO, BIN/CUE and lossless single-track CD CHD are accepted.
Other regions, Xbox copies and modified discs are not supported.

Extract the ZIP into a writable folder and run MOJO.exe, then select your disc.
Initial setup downloads verified open-source compiler/runtime dependencies and
builds locally. RecompLauncher is optional and calls the same Level 3 prepare
interface. See README.md and docs/VALIDATION.md for installation and actual test scope.

Updating preserves userdata, including saves, settings and the supplied disc copy.
Back it up first. No generated game executable or proprietary assets are included.
This is a release candidate: a full playthrough, broader hardware coverage and
desktop RecompLauncher qualification remain documented validation work.
