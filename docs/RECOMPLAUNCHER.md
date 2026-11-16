# RecompLauncher integration

The format-1 manifest implements Level 1 launch, Level 2 settings/save paths,
and Level 3 headless preparation. Both launch paths call the same builder.
`prepare` emits `progress <0..1> <message>`, exits nonzero on failures, and has
a 7200-second timeout. The underlying build step has a 3600-second timeout.
No settings window or game window is opened during preparation.

Setup accepts ISO, lossless single-track CD CHD, and CUE with its matching BIN
for the original USA PS2 disc described in COMPATIBILITY.md. The launcher
checks the serial when it can read one. The builder normalizes the image and
enforces exact disc and boot executable SHA-256 validation for every format.
The launcher's raw ISO9660 check would reject CUE and CHD before that step.
Verified-copy sizes and CRC32 values come from the SHA-256-matching project
reference documented in COMPATIBILITY.md. They are not claimed as independent
Redump certification; exact SHA-256 validation remains mandatory in the builder.

Native preview packages select Linux/macOS executable paths and macOS's external
data directory during packaging. They retain the same Level 3 protocol and all
settings. See PLATFORMS.md for prerequisites and test boundaries. GitHub
prereleases require RecompLauncher's service to enable a catalog beta; publishing
one does not automatically switch stable users to the experimental build.

Launcher's JSON settings are separate from upstream controller bindings. New
defaults only are supplied, so updates preserve player choices. Save declarations
include memory cards and settings only. Private build/runtime logs are deliberately
not registered as diagnostic attachments; use the sanitized diagnostics command.

**Upscale 2D artwork** uses the same `upscale_hud` key in `userdata/saves/keys.ini`
as **Upscale 2D** in F1. It defaults to Off and takes effect on the next launch
at Enhanced rendering resolution or higher. The GPU reconstructs HUD, menu,
and startup artwork from the player's disc. RecompLauncher downloads the same
builder archive used for standalone setup.

Big Picture starts fullscreen. Console-specific key inputs, mods, multi-game
selection and achievements are inapplicable or unimplemented. Controller glyph
replacement is not attempted inside the original game. RecompAchievements could
be investigated later: https://github.com/elripalda/RecompAchievements.

The desktop Setup and Play flow was exercised through **Add From GitHub or
GitLab** in beta 37. The Developer tab's **Check** action was unavailable to the
test account. See VALIDATION.md for the executed checks. The RecompStore
submission was received for review. The catalog listing and Easy Setup badge
are controlled by RecompStore and can be followed at https://recompstore.com/hub.

The v1.1.0 queue and page-clear optimizations are automatic internal runtime
changes. Existing launcher settings and save paths are unchanged. A new pipeline
identifier makes either installation method rebuild the native runtime locally;
no copyrighted generated executable is downloaded in the update.
