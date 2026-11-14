# Release gate

1. Test synthetic checks and the manifest schema. Run local disc tests privately.
2. Build helper-only ZIP with scripts/package.ps1. No game is required.
3. Run Gitleaks against clean source, staging and all history with full redaction.
4. Run verify_publication.py --git and --archive on the exact artifact.
5. Inspect helper PE strings for private paths; verify dependency notices.
6. Review the explicit file list, Git author metadata and all refs before push.
7. Push ordinary commits to the existing repository and verify remote content.
   For a new repository, start private until the owner approves public visibility.
8. Publish the versioned release with the exact supported disc table and test
   limitations. Mark experimental builds as prereleases; stable releases require
   passed regression checks and an owner playtest.

The ZIP includes original source for the helper wrappers and the libchdr license
notices; libchdr's pinned upstream source remains available at docs/SOURCES.md.
Never attach userdata, build caches, game executables or raw test evidence.
GitHub Secret Scanning and Push Protection availability depends on repository and
account features. Enable them where available; record unavailable controls explicitly.
Only the owner can authorize changing repository visibility to public.
