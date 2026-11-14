# Building and maintaining

Source checkout needs Windows PowerShell 5.1, internet and a writable folder.
`Start-MOJO.cmd -Game "D:\Games\Mojo.iso"` fetches verified tools and builds the
game locally. `-Prepare` builds without opening the game. `-Smoke` runs a bounded
3100-frame headless boot. The normal release uses `MOJO.exe` for a file picker.
For CHD input from a source checkout, first run the packaging command below and
use its extracted portable ZIP, which includes the compiled CHD helper.

Build distributable helpers and a release with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/package.ps1
```

This fetches pinned upstream source/toolchain and libchdr, builds only the original
bootstrap and CHD reader, runs the publication verifier, and writes a ZIP to
`dist/`. It never invokes the game recompiler or needs a disc. Release packaging
uses an explicit source file allowlist plus two known helper executables.
Packaging fetches only Clang, CMake, Ninja and Python through upstream's existing
hash-checked downloader. It does not need MinGit or BusyBox. First-time game
setup still uses upstream's complete portable toolchain.

Use `python scripts/verify_publication.py` before committing. Install Gitleaks
and run `gitleaks dir . --redact=100` on a clean checkout, then `gitleaks git .
--redact=100` for history. Never run either scanner with raw secret reporting.
Enable the local hook with `git config core.hooksPath .githooks`.

Create release tags only after local game tests and a clean security review.
The workflow builds and scans public components using synthetic tests; commercial
disc images are never uploaded to CI. See `docs/RELEASING.md` for audit scope.
