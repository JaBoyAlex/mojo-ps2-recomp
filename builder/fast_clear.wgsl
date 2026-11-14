// The host proves full-page coverage and constant results before dispatch.
@compute @workgroup_size(64)
fn fast_clear(@builtin(global_invocation_id) gid: vec3<u32>) {
    let i = gid.x + gid.y * 64u * 1024u;
    if (i < prm(1u) && prm(3u) != 0xFFFFFFFFu) {
        let word = prm(0u) + i;
        let mask = prm(3u);
        var value = prm(2u);
        if (mask != 0u) { value = (atomicLoad(&vram[word]) & mask) | (value & ~mask); }
        atomicStore(&vram[word], value);
    }
    if (i < prm(5u)) { atomicStore(&vram[prm(4u) + i], prm(6u)); }
}
