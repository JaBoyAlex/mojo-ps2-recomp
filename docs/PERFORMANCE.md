# Conservative performance work

Research reviewed 2026-11-14. The priority is preserving the verified MOJO!
gameplay, including movement, camera controls, graphics, audio and saves.

## Research and scope

- [ps2-native-recomp releases](https://github.com/exoteric33/ps2-native-recomp/releases):
  the experimental hardware renderer is explicitly described as slower than the
  default and capable of exhausting memory. Keep the pinned compute renderer.
- [PCSX2 2.8 technical report](https://github.com/PCSX2/pcsx2-net-www/blob/main/blog/2026/pcsx2-2.8/index.mdx):
  avoiding unnecessary texture copies and GPU readbacks can help particular games,
  but depends on proving texture hazards and invalidation correct. These changes
  are renderer-specific; they are not drop-in optimizations for this runtime.
- [OpenGOAL methodology](https://github.com/open-goal/jak-project#project-description):
  its native compiler and game-specific decompilation target Naughty Dog's GOAL
  language. They cannot be applied directly to this MIPS recompilation pipeline.
- [PS2Recomp](https://github.com/ran-j/PS2Recomp): another compiler/runtime
  architecture, reviewed for context. Changing frameworks would require broad
  compatibility work. No code from it or PCSX2 was copied into this project.

Existing CPU sampling identifies queue posting among active host functions, but
is not a whole-process profile and includes time waiting on other threads.
Keep PS2 floating-point behavior, cycle counts, audio scheduling, graphics
synchronization, texture invalidation and compiler optimization flags intact.

## Exact page clears (v1.1.0)

Profiling the supported MOJO! scene found that rasterization dominated GPU time.
The optimization recognizes an untextured sprite covering complete physical GS
pages, then writes the exact packed color/depth to those pages in one linear
compute dispatch. All internal-resolution samples receive the same result.
It preserves framebuffer masks, FBA, depth writes and the proved identity blend.

The guard requires integer, full-width, page-aligned coverage with a matching
scissor, supported 32-bit formats, no destination/conditional tests, no wrapping
and no framebuffer/depth aliasing. Other draws use the existing rasterizer.
The existing page tracking and batching reset are retained. Atomic VRAM accesses,
texture invalidation, timing, simulation and floating-point behavior are unchanged.
The automatic optimization needs no new F1 or RecompLauncher setting.
`PS2_FAST_CLEAR=0` disables it when launching the generated runtime directly
for developer comparisons; the normal bootstrap resets diagnostic overrides.

Research also examined [the God of War native port's performance work](https://github.com/Waffle565/God-Of-War-Native-Port/blob/main/docs/performance.md),
[RAC-RS](https://github.com/AsobiCodes/rac-rs), and
[RAC-Native](https://github.com/RAC-Native/rac1-native-game/blob/main/docs/status.md).
These supplied architectural context, not copied implementation. Changes to
floating-point approximations, emulation cycle counts, pipeline synchronization
or the renderer architecture were excluded. Tile-size changes, triangle/sprite
shader specialization, non-atomic stores and decoded-texture experiments did not
establish sufficient benefit or equivalence and are not included.

Native tests compile the actual production guard and cover 433 parameter and
negative cases, plus 65,536 exact byte-color blend identities. The optional
`tests/fast_clear_gpu.cpp` fixture draws synthetic GS state into randomized VRAM:
24 cases at each of four scales, comparing the entire graphics memory with the
optimization disabled/enabled. All 96 comparisons matched. It uses no game data.
The release packaging and CI run the CPU guard tests; the GPU differential test
was executed locally on the documented D3D12 test host.

An early stress harness combined `PS2_TIME` and `PS2_THREADS=1`, causing intermittent
GPU device loss with the optimization both disabled and enabled. Source inspection
found that the timing diagnostic flushes GPU state from the simulation thread;
the window path disables threading when that diagnostic is active. This
combination is excluded from qualification and benchmark results. Six repeated
multithreaded stress runs without the timing diagnostic passed, alternating the
optimization off/on. No speculative submission-fence change is included.

## Final v1.1.0 measurements against rc.7

Windows 11, Core i5-11400, RTX 3060 Ti, 32 GB RAM, D3D12, High internal
resolution (1920x1344), Upscale 2D On. Both games used the same Stage 1 state.
Three alternating-order pairs were run for each method. Values are medians of
run averages, not claims about other PCs.

| Measurement | rc.7 | v1.1.0 | Observed change |
| --- | ---: | ---: | ---: |
| Normal-speed windowed FPS | 60.05 | 60.07 | approximately 0% |
| Process CPU ms/frame in normal play | 7.008 | 6.755 | 3.6% less |
| Uncapped single-threaded headless frames/s | 134.41 | 153.85 | 14.5% higher |
| Sampled GPU kernel ms/frame, headless profiling | 7.314 | 7.068 | 3.4% less |

The windowed runs each covered 1200 emulated frames, about 20 seconds, with the
first 150 excluded. They retained ordinary pacing and used scripted ball motion.
Normal-speed 1%-low values ranged from 59.62 to 59.74 FPS for rc.7 and
59.66 to 59.77 FPS for v1.1.0. This short scene does not establish better stutter
or worst-case behavior throughout the game.

The headless throughput test timed 1200 frames after 350 warmup frames, with the
same scripted motion. It used `PS2_TIME=2800,1200` without `PS2_THREADS` to keep
the timing diagnostic on its supported single-threaded path. Its faster rates
measure uncapped processing capacity; they do not represent normal gameplay
speed, presented frames, or the multithreaded player's frame rate. No unlocked
speed option or pacing change ships in normal play.

GPU timestamps separately sampled 300 frames after warmup in a stationary Stage
1 view, summing upload, raster, palette, decode and clear kernels. They exclude
presentation and CPU time; profiling changes submission behavior. The final GPU
result is smaller than the preliminary frame-capture profiling result and is the
number reported for the final build. The throughput gain must not be described
as an equivalent percentage reduction in GPU time.

There is no defensible FPS percentage for "most people" from one PC and scene.
Players already at 60 FPS should expect approximately 0% additional FPS. Slower
PCs may benefit when the optimized work is a bottleneck, but require direct tests.

## Queue offsets

The render and vector queues each allocate 32 MiB in the pinned runtime.
For unsigned cursors and a power-of-two capacity, `cursor % capacity` equals
`cursor & (capacity - 1)`. Compute the mask once when the ring starts and use
it at the three buffer-offset sites. Retain division for other capacities.
Buffer sizes, packet layout, atomics, memory ordering and wakeups are unchanged.
The builder pipeline identifier changes so an existing install rebuilds through
the same standalone and RecompLauncher prepare interface.

The synthetic native test compiles the actual patched queue implementation.
It checks ordered payloads, zero-length payloads, wraparound at several capacities,
non-power-of-two fallback, and a producer/consumer pair at the production capacity.
This tests offsets and packet integrity; it does not qualify queue liveness under
arbitrary saturation. Benchmark timings are informational and are not CI limits.

Five alternating-order pairs on the existing Windows 11 test host measured the
median time for ten million synthetic post/peek/pop cycles as 255.053 ms before
and 240.727 ms after, approximately 5.6% less time in that isolated workload.
This is not a claim of a 5.6% frame-rate increase or reduced total CPU usage.
Results on other hardware may differ.

## Earlier queue-only windowed comparison against rc.7

Windows 11, Core i5-11400, RTX 3060 Ti, 32 GB RAM, Direct3D 12, High internal
resolution (1920x1344), Upscale 2D enabled. Three alternating-order pairs used
the same Stage 1 state and scripted inputs. Each run covered 1200 emulated
frames, about 20 seconds at normal speed; the first 150 frames were excluded.
The following values are the medians of the three run averages:

| Measurement | rc.7 | Candidate | Change |
| --- | ---: | ---: | ---: |
| Normal-speed FPS | 60.0074 | 60.0089 | approximately 0% |
| Uncapped benchmark FPS | 161.5792 | 161.5372 | -0.03% |
| Process CPU time per frame, normal speed | 7.0232 ms | 6.9190 ms | -1.5% |
| Process CPU time per frame, uncapped | 6.6808 ms | 6.5321 ms | -2.2% |

Uncapped mode disabled pacing and requested immediate presentation only in the
benchmark environment. Normal play retains its limiter and ordinary presentation.
These are emulated-frame rates recorded by the existing runtime, not an external
monitor measurement. The samples include process CPU time and exclude shader
startup from the measured interval. There was substantial run-to-run variation,
including a transient hitch in the first candidate window run. Normal-speed
1%-low values ranged from 50.67 to 59.66 FPS for rc.7 and 9.43 to 59.75 for the
candidate; the data does not establish improved stutter or frame pacing.

The throughput difference is negligible. CPU savings are small observed values,
not a reliable population estimate. There is no defensible percentage FPS gain
for "most people" from this single host and scene. Players already at the frame
limit should expect about 0% FPS gain; CPU-limited PCs require their own tests.

## Regression checks

- All 206 checkpoints of the 3100-frame boot replay matched, independently on
  single-threaded and three-threaded paths. The audio output matched rc.7 byte
  for byte in each path.
- Four ball-movement frames at each of four internal resolutions, with Upscale
  2D both Off and On, were pixel-identical to rc.7: 32 compared frame pairs.
- Seven synthetic Python tests passed. The real native queue tests passed at
  seven capacities, including non-power-of-two arithmetic and production-size
  producer/consumer ordering. The patch applied twice without duplicate edits.
- The shared headless prepare interface upgraded an isolated rc.7 install and
  a subsequent standalone launch completed 3100 frames. Disc, memory card,
  camera/HUD preferences and display settings hashes were unchanged. The old
  runtime was retained.

The queue-only work was held before publishing v1.0.0 and is included in the
v1.1.0 release, retaining rc.7 as the previous published release. The owner completed the requested approximately five-minute
normal-speed playtest and reported no issues noticed. A full playthrough and
broader hardware qualification remain open; this is not a claim of full-game
compatibility on every supported Windows system.
