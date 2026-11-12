// Edge-adaptive kernel based on FidelityFX FSR 1 EASU, adapted for straight-alpha
// GS textures. Copyright (c) 2021 Advanced Micro Devices, Inc.
// See licenses/fidelityfx-fsr.txt.
var<private> hud_min: vec2<i32>;
var<private> hud_max: vec2<i32>;

fn hud_tap(s: Setup, uv: vec2<i32>, k: u32) -> u32 {
    // Each glyph occupies part of an atlas. Extra taps must stay on its side
    // of the boundary even when the GS texture is configured to wrap.
    let p = clamp(uv, hud_min, hud_max);
    return fetch(s, p.x, p.y, k);
}

fn hud_color(raw: u32, uses_alpha: bool) -> vec4<f32> {
    let c = unpack4(raw);
    let alpha = select(128.0, c.a, uses_alpha);
    return vec4<f32>(c.rgb * (alpha / 128.0), alpha);
}

fn hud_edge(top: f32, left: f32, center: f32, right: f32, bottom: f32) -> vec3<f32> {
    let gradient = vec2<f32>(right - left, bottom - top);
    let range = max(abs(vec2<f32>(right, bottom) - center), abs(vec2<f32>(left, top) - center));
    let strength = min(abs(gradient) / max(range, vec2<f32>(1.0)), vec2<f32>(1.0));
    return vec3<f32>(gradient, dot(strength, strength));
}

const HUD_OFFSETS = array<vec2<i32>, 12>(
    vec2<i32>(0, 0), vec2<i32>(1, 0), vec2<i32>(0, 1), vec2<i32>(1, 1),
    vec2<i32>(0, -1), vec2<i32>(1, -1), vec2<i32>(-1, 0), vec2<i32>(2, 0),
    vec2<i32>(-1, 1), vec2<i32>(2, 1), vec2<i32>(0, 2), vec2<i32>(1, 2),
);

fn sample_hud(s: Setup, uin: f32, vin: f32, k: u32) -> u32 {
    let uv = vec2<f32>(uin, vin) - 0.5;
    let ij = vec2<i32>(floor(uv));
    let f = fract(uv);
    let a = hud_tap(s, ij, k);
    let b = hud_tap(s, ij + vec2<i32>(1, 0), k);
    let c = hud_tap(s, ij + vec2<i32>(0, 1), k);
    let d = hud_tap(s, ij + vec2<i32>(1, 1), k);
    // The bounded kernel returns the same value on flat texture regions.
    if (a == b && a == c && a == d) {
        return a;
    }
    var color: array<vec4<f32>, 12>;
    let uses_alpha = has(s, F_TCC);
    color[0] = hud_color(a, uses_alpha);
    color[1] = hud_color(b, uses_alpha);
    color[2] = hud_color(c, uses_alpha);
    color[3] = hud_color(d, uses_alpha);
    for (var i = 4u; i < 12u; i = i + 1u) {
        color[i] = hud_color(hud_tap(s, ij + HUD_OFFSETS[i], k), uses_alpha);
    }
    return reconstruct_2d(color, f);
}

fn sample_uploaded_picture(gid: vec2<u32>) -> u32 {
    let uv = (vec2<f32>(gid) + 0.5) / f32(SCALE) - 0.5;
    let ij = vec2<i32>(floor(uv));
    let upper = vec2<i32>(i32(prm(5u)) - 1, i32(prm(6u)) - 1);
    let origin = vec2<u32>(prm(3u), prm(4u));
    let bp = prm(0u);
    let bw = prm(1u);
    var color: array<vec4<f32>, 12>;
    for (var i = 0u; i < 12u; i = i + 1u) {
        let p = origin + vec2<u32>(clamp(ij + HUD_OFFSETS[i], vec2<i32>(0), upper));
        color[i] = hud_color(read_pixel(PSMCT32, bp, bw, p.x, p.y), false);
    }
    return reconstruct_2d(color, fract(uv));
}

fn reconstruct_2d(color: array<vec4<f32>, 12>, f: vec2<f32>) -> u32 {
    var guide: array<f32, 12>;
    for (var i = 0u; i < 12u; i = i + 1u) {
        guide[i] = dot(color[i], vec4<f32>(0.25, 0.5, 0.25, 1.0));
    }

    let tl = hud_edge(guide[4], guide[6], guide[0], guide[1], guide[2]);
    let tr = hud_edge(guide[5], guide[0], guide[1], guide[7], guide[3]);
    let bl = hud_edge(guide[0], guide[8], guide[2], guide[3], guide[10]);
    let br = hud_edge(guide[1], guide[2], guide[3], guide[9], guide[11]);
    let edge = mix(mix(tl, tr, f.x), mix(bl, br, f.x), f.y);
    let dir = normalize(select(vec2<f32>(1.0, 0.0), edge.xy, dot(edge.xy, edge.xy) > 0.001));
    let strength = edge.z * edge.z * 0.25;
    let stretch = 1.0 / max(abs(dir.x), abs(dir.y));
    let axes = mix(vec2<f32>(1.0), vec2<f32>(stretch, 0.5), strength);
    let lobe = mix(0.5, 0.21, strength);
    var accum = vec4<f32>(0.0);
    var weight = 0.0;
    for (var i = 0u; i < 12u; i = i + 1u) {
        let offset = vec2<f32>(HUD_OFFSETS[i]) - f;
        let rotated = vec2<f32>(dot(offset, dir), dot(offset, vec2<f32>(-dir.y, dir.x))) * axes;
        let radius2 = min(dot(rotated, rotated), 1.0 / lobe);
        let kernel = 0.4 * radius2 - 1.0;
        let window = lobe * radius2 - 1.0;
        let w = (1.5625 * kernel * kernel - 0.5625) * window * window;
        accum += color[i] * w;
        weight += w;
    }
    let lo = min(min(color[0], color[1]), min(color[2], color[3]));
    let hi = max(max(color[0], color[1]), max(color[2], color[3]));
    // Bound ringing at sharp outlines and restore the GS straight-alpha format.
    let col = clamp(accum / max(weight, 0.001), lo, hi);
    let rgb = col.rgb * (128.0 / max(col.a, 0.0001));
    let rgba = vec4<u32>(clamp(vec4<f32>(rgb, col.a) + 0.5, vec4<f32>(0.0), vec4<f32>(255.0)));
    return rgba.x | (rgba.y << 8u) | (rgba.z << 16u) | (rgba.w << 24u);
}
