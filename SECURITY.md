# Security and privacy

Do not post credentials, private logs, disc images, generated game code or dumps
in issues. Use GitHub private vulnerability reporting when enabled; if it is
unavailable, ask for a private contact without revealing the vulnerability or secret.

Publication requires an explicit file allowlist, independent privacy/proprietary
checks, Gitleaks tree and history scans, archive inspection and binary-string review.
Any unresolved secret/privacy/copyright finding blocks publication. `.gitignore`
is only a convenience, not an audit. Scan every ref intended for push. Keep scans
redacted. Never inspect unrelated browser profiles or credential stores to audit.

The builder reads untrusted images only through bounded importers and verifies
exact hashes before recompilation. Downloads use HTTPS and pinned hashes. Generated
game code is trusted only to the extent the supported local disc is trusted.
Builds require no elevation. Unsigned helper binaries may trigger SmartScreen.

The privacy scanner has one narrow binary exception: six exact public CI source
paths embedded in the pinned LLVM libc++abi static library in MOJO.exe. These
refer to LLVM's GitHub runner, not any user's machine. The six filenames and full
prefix are enumerated in the verifier; other home paths remain errors. There are
no broad secret-scanner suppressions.
