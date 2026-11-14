# Troubleshooting

- **Wrong image (20):** only the USA PS2 serial/revision and exact normalized hash
  in COMPATIBILITY.md work. Modified, truncated and other-region discs are refused.
  Keep BIN/CUE together. For CHD, use a lossless single-track CD without a parent.
- **Dependencies/write access (21):** use a writable local folder outside Program
  Files, free at least 5 GB, check network access, and retry. No administrator
  permission is required. A read-only portable folder is not supported.
  The upstream BusyBox download host has intermittently returned HTTP 403 or
  timed out. Retry setup when it is reachable; cached tools are reused. Retain
  the pinned checksums rather than substituting an unverified executable.
- **Compilation (22):** close other heavy workloads and retry. Upstream's bounded
  compile parallelism is at most six jobs. Do not upload raw logs from userdata/cache.
- **Timeout (23):** rerun setup; downloaded tools are reused. Cancellation releases
  the lock and kills descendant processes when using MOJO.exe.
- **Already running (24):** close the other game/build process for this installation.
- **Graphics:** update GPU drivers. D3D12 is tested; do not assume all Vulkan or
  software-renderer configurations have equivalent performance.
- **Flicker:** report stage, movement direction, display mode and rendering setting.
  No flicker was seen in the current user playtest, but not every scene is tested.
- **Saves:** back up userdata/saves. Never overwrite an existing memory card with
  a blank one. Quick states and in-game card saves are different features.

Run `python scripts/diagnostics.py` to print a deliberately small, sanitized status
report. It excludes local paths, environment variables, usernames and raw logs.
