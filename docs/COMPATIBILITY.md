# Supported copy and evidence

| Field | Verified reference |
| --- | --- |
| Platform / region | PlayStation 2 / USA (NTSC) |
| Boot executable | `SLUS_207.41` (serial SLUS-20741) |
| SYSTEM.CNF VER | `1.02` |
| Raw BIN size | 130926432 bytes |
| Raw layout | One MODE2/2352 data track, INDEX 01 00:00:00 |
| BIN SHA-256 | `c08a5f5811efddcdf3f06ab3e8212fae622e9d4613adabb8a47b5a88280b6432` |
| Normalized ISO SHA-256 | `bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5` |
| Boot ELF SHA-256 | `b749b3765aa3c74d594ec502686246965b69e8492c49ac08f5283a245adc8a60` |

These values were computed from the locally tested user-provided disc. They are
not claimed to be independently certified Redump records. No official retail
revision label beyond the observed disc metadata is asserted. CUE formatting and
CHD compression vary, so the builder verifies their decoded ISO, not their container
hash. CHDs with parent dependencies, multiple tracks or stored gaps are rejected.

## Existing playable build

- User playtest: progressed beyond round 10 without observed bugs; no movement flicker reported.
- Automated: cold boot to gameplay, 291 movement-frame captures, collisions and block removal.
- D3D12 versus software renderer comparison over 70 frames: largest channel MAE
  0.0054385 on a 0–255 scale; this is evidence for the tested scene, not all scenes.
- 206 deterministic replay checkpoints matched in the existing build.
- Upstream memory-card filesystem, ECC, atomic persistence and recovery tests passed.
- Real game progression save/load across restarts has not yet been verified.
- Audio samples were produced; full auditory fidelity has not been established.

## Environment and limitations

Tested: Windows 11 x64, NVIDIA RTX 3060 Ti, D3D12, 8BitDo Ultimate 2C controller.
This is not a minimum specification. No broad performance benchmark, clean VM,
Steam Deck, Linux, macOS, AMD or Intel GPU qualification has been completed.
The runtime approximates PS2 timing and interprets IOP code. Previously unseen
EE/VU code may incur compilation pauses. A complete game playthrough remains open.
Other regions and revisions fail closed until separately verified and tested.

See `VALIDATION.md` for the publication builder's executed test results.
