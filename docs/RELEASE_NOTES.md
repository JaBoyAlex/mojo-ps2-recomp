# MOJO! Recomp 1.0.0-rc.4 — Windows x64 portable builder

RecompLauncher setup now passes CUE/BIN and CHD to the builder for exact disc
validation. For CUE/BIN, select the CUE and keep its matching BIN beside it.
The native gameplay pipeline and independent F1 camera controls are the same as
rc.3.

This archive contains a builder and open-source helper tools, not the game.
Supply your own **MOJO! USA PlayStation 2 disc, SLUS_207.41, SYSTEM.CNF VER 1.02**.
Only the exact normalized ISO SHA-256
`bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5`
is supported. ISO, BIN/CUE and lossless single-track CD CHD are accepted.
Other regions, Xbox copies and modified discs are not supported.

Extract the ZIP into a writable folder and run MOJO.exe, then select your disc.
Initial setup downloads verified open-source compiler/runtime dependencies and
builds locally. RecompLauncher is optional and calls the same Level 3 prepare
interface. Desktop GitHub install, automatic ISO setup and Play were verified
with rc.3. CUE/BIN setup and Play passed with the corrected manifest in the
same test installation. See README.md and docs/VALIDATION.md for details.

Updating preserves userdata, including saves, settings and the supplied disc copy.
Back it up first. No generated game executable or proprietary assets are included.
This is a release candidate. A full playthrough and broader hardware coverage
remain open.
