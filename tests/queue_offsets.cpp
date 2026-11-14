// Exercise the real upstream queue with synthetic messages only.
#include "gs/queue.hpp"
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
using namespace ps2::gs::queue;
void check(bool ok) { if (!ok) std::abort(); }
int main() {
    std::setbuf(stdout, nullptr);
    constexpr unsigned count = 20000;
    for (auto capacity : {512u, 528u, 4096u, 4112u, 1u << 20, 4u << 20, 32u << 20}) {
        Ring ring;
        ring.start(capacity);
        auto produce = [&](unsigned i) {
            std::array<unsigned char, 127> bytes{};
            bytes.fill(static_cast<unsigned char>(i));
            ring.post(kGif, i, ~i, bytes.data(), i % bytes.size());
        };
        const bool concurrent = capacity == (32u << 20);
        std::thread producer([&] {
            if (!concurrent) return;
            std::array<unsigned char, 127> bytes{};
            for (unsigned i = 0; i < count; ++i) {
                bytes.fill(static_cast<unsigned char>(i));
                ring.post(kGif, i, ~i, bytes.data(), i % bytes.size());
            }
        });
        for (unsigned i = 0; i < count; ++i) {
            if (!concurrent) produce(i);
            Header h{};
            const std::uint8_t *bytes;
            while (!ring.peek(h, bytes)) std::this_thread::yield();
            check(h.type == kGif && h.arg0 == i && h.arg1 == ~i && h.bytes == i % 127);
            for (unsigned j = 0; j < h.bytes; ++j) check(bytes[j] == static_cast<unsigned char>(i));
            ring.pop(h);
        }
        producer.join();
        check(ring.empty());
        std::printf("capacity %u: %u ordered variable-size packets verified\n", capacity, count);
    }
    Ring ring;
    ring.start(1u << 20);
    auto start = std::chrono::steady_clock::now();
    for (unsigned i = 0; i < 10000000; ++i) {
        ring.post(kGif, i, 0, nullptr, 0);
        Header h{};
        const std::uint8_t *p;
        check(ring.peek(h, p) && h.arg0 == i);
        ring.pop(h);
    }
    std::printf("benchmark_ms %.3f\n", std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count());
}
