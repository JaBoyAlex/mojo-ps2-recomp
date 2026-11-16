#pragma once
#include <chrono>
#include <cstdint>

namespace mojo::host_clock {
// Scheduling and audio delivery use steady (CLOCK_MONOTONIC) time. A virtual
// machine's raw hardware clock can run at a different rate from that clock;
// mixing them makes sound pacing and reported frame rates disagree.
inline std::uint64_t counter() {
    return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
}
inline constexpr std::uint64_t frequency() { return 1000000000ull; }
}
