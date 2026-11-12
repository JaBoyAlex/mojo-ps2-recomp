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
Verified-dump metadata is omitted because no independent Redump record was verified.

Launcher's JSON settings are separate from upstream controller bindings. New
defaults only are supplied, so updates preserve player choices. Save declarations
include memory cards and settings only. Private build/runtime logs are deliberately
not registered as diagnostic attachments; use the sanitized diagnostics command.

**Upscale HUD** uses the same `upscale_hud` key in `userdata/saves/keys.ini` as F1.
It is off by default and applies on the next launch at Enhanced rendering
resolution or higher. The GPU reconstructs HUD texels in memory from the
player's own disc during play. RecompLauncher downloads the same code-only
builder archive used for standalone setup. Neither path needs a texture pack.

Big Picture starts fullscreen. Console-specific key inputs, mods, multi-game
selection and achievements are inapplicable or unimplemented. Controller glyph
replacement is not attempted inside the original game. RecompAchievements could
be investigated later: https://github.com/elripalda/RecompAchievements.

The desktop Setup and Play flow was exercised through **Add From GitHub or
GitLab** in beta 37. The Developer tab's **Check** action was unavailable to the
test account. See VALIDATION.md for the executed checks. The RecompStore
submission was received for review. The catalog listing and Easy Setup badge
are controlled by RecompStore and can be followed at https://recompstore.com/hub.
