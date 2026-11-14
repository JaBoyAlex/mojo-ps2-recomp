// Exact page-aligned untextured sprite clears. Unsupported cases keep the rasterizer.
bool try_fast_clear() {
    Batch &b = g_batch;
    if (!g_fast_clear || g_live || hwcache::g_on || stat::g_on || g_batch_log || g_bench.capturing ||
        !g_batch_reads.empty() || b.prims.size() != kPrimWords || b.fpsm != PSMCT32 || b.zpsm != PSMZ32 ||
        !b.fbw || b.minx != 0 || b.miny < 0 || (b.miny & 31) || ((b.maxy + 1) & 31) || b.maxx != int(b.fbw * 64u) - 1) return false;
    const auto *p = b.prims.data();
    if ((p[1] & kKindMask) != 1 || p[0] >= b.setups.size() / kSetupWords) return false;
    const auto *w = b.setups.data() + p[0] * kSetupWords;
    const unsigned flags = w[0], modes = w[7];
    if ((flags & (2u | 4u | 128u)) || (modes >> 28 & 3u) ||
        ((flags & 64u) && (modes & 7u) != 1u) || ((flags & 512u) && (modes >> 8 & 3u) != 1u)) return false;
    if (w[1] != b.fbp || w[2] != b.fbw || w[3] != PSMCT32 || w[5] != b.zbp || w[6] != PSMZ32) return false;
    if (u2f(p[4]) != 0.0f || u2f(p[5]) != float(b.miny) || u2f(p[6]) != float(b.fbw * 64u) ||
        u2f(p[7]) != float(b.maxy - b.miny + 1)) return false;
    if (int(w[10] & 0xffffu) > b.minx || int(w[10] >> 16) < b.maxx ||
        int(w[11] & 0xffffu) > b.miny || int(w[11] >> 16) < b.maxy) return false;
    unsigned color = p[13], alpha = color >> 24;
    if ((flags & 8u) && (!(flags & 1024u) || (alpha & 128u))) {
        // (Cs-Cd)*128/128+Cd == Cs exactly for byte colors, with no rounding remainder.
        if (alpha != 128u || (modes >> 12 & 3u) != 0u || (modes >> 14 & 3u) != 1u ||
            (modes >> 16 & 3u) != 0u || (modes >> 18 & 3u) != 1u) return false;
    }
    if (flags & 4096u) color |= 0x80000000u;
    const bool depth = (flags & 512u) && !(flags & 32u);
    const Range fb = pages(b.fbp, b.fbw, b.fpsm, b.minx, b.miny, b.maxx, b.maxy);
    const Range zb = pages(b.zbp, b.fbw, b.zpsm, b.minx, b.miny, b.maxx, b.maxy);
    if (fb.hi > kMemorySize || zb.hi > kMemorySize || (depth && fb.overlaps(zb.lo, zb.hi))) return false;
    const unsigned layers = g_scale * g_scale;
    const unsigned words = unsigned((fb.hi - fb.lo) / 4) * layers;
    const unsigned zwords = depth ? unsigned((zb.hi - zb.lo) / 4) * layers : 0u;
    dispatch_linear(kFastClear, std::max(words, zwords), push_params({unsigned(fb.lo / 4) * layers, words, color, w[4],
                    unsigned(zb.lo / 4) * layers, zwords, std::min(p[24], w[23])}));
    mark_rendered(fb);
    if (b.zwrite) mark_rendered(zb);
    ++g_fast_clears;
    reset_batch();
    return true;
}
