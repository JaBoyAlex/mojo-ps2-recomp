# RecompLauncher integration

The format-1 manifest implements Level 1 launch, Level 2 settings/save paths,
and Level 3 headless preparation. Both launch paths call the same builder.
`prepare` emits `progress <0..1> <message>`, exits nonzero on failures, and has
a 7200-second timeout. The underlying build step has a 3600-second timeout.
No settings window or game window is opened during preparation.

Setup accepts the original USA PS2 disc described in COMPATIBILITY.md. The
serial is only an initial launcher check: the builder then enforces exact SHA-256
validation. A `game.dumps` badge is intentionally omitted because no independent
Redump record has been verified. Known local hashes are fully documented instead.

Launcher's JSON settings are separate from upstream controller bindings. New
defaults only are supplied, so updates preserve player choices. Save declarations
include memory cards and settings only. Private build/runtime logs are deliberately
not registered as diagnostic attachments; use the sanitized diagnostics command.

Big Picture starts fullscreen. Console-specific key inputs, mods, multi-game
selection and achievements are inapplicable or unimplemented. Controller glyph
replacement is not attempted inside the original game. RecompAchievements could
be investigated later: https://github.com/elripalda/RecompAchievements.

Desktop developer-mode UI testing and catalog publication are separate from
manifest/protocol tests. Beta 37 restricts the Developers tab to verified developer
accounts (or qualifying existing local builds); the test account did not expose
this tab. No verification or account restrictions were bypassed. See VALIDATION.md
for the actual tested scope. A project
maintainer can claim the project through https://recompstore.com/hub using GitHub
sign-in. That external account action has not been performed automatically.
