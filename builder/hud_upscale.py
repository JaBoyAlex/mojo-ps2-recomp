"""Opt-in subpixel sampling for native-size HUD overlays in the pinned runtime."""
import importlib.util
from pathlib import Path


def apply(engine):
    spec = importlib.util.spec_from_file_location(
        'display_labels', Path(__file__).with_name('display_labels.py'))
    labels = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(labels)
    replace = labels.replace_once

    keymap = engine / 'host/keymap.cpp'
    keymap_header = engine / 'host/keymap.hpp'
    menu = engine / 'host/quickmenu.cpp'
    menu_header = engine / 'host/quickmenu.hpp'
    window = engine / 'host/window.cpp'
    gpu = engine / 'runtime/src/gs/gpu/gpu.cpp'
    shader = engine / 'runtime/src/gs/gpu/gs.wgsl'

    replace(keymap_header, '    bool right_stick_invert_y = false;',
            '    bool right_stick_invert_y = false;\n    bool upscale_hud = false;')
    replace(keymap_header, 'Config defaults();', '''Config defaults();
std::string with_upscale_hud(const std::string &text, bool enabled);''')
    replace(keymap, '        if (name == "sharp2d") {', '''        if (name == "upscalehud") {
            const std::string v = squash(value);
            if (v == "on") config.upscale_hud = true;
            else if (v == "off") config.upscale_hud = false;
            else bad("upscale_hud is on or off, ignored");
            continue;
        }
        if (name == "sharp2d") {''')
    replace(keymap, 'std::string with_sharp_2d(', '''std::string with_upscale_hud(const std::string &text, bool enabled) {
    return with_line(text, "upscalehud", std::string("upscale_hud = ") + (enabled ? "on" : "off"));
}

std::string with_sharp_2d(''')
    replace(menu_header, 'sharp_2d, fullscreen,', 'sharp_2d, upscale_hud, fullscreen,')
    replace(menu_header, '    bool sharp_locked = false;', '''    bool upscale_hud_now = false, upscale_hud_next = false;
    bool sharp_locked = false;''')
    replace(menu, 'constexpr int kEntries = 12;', 'constexpr int kEntries = 13;')
    replace(menu, 'Command::sharp_2d, Command::fullscreen,', 'Command::sharp_2d, Command::upscale_hud, Command::fullscreen,')
    replace(menu, '{"F1", "F5", "F8", "F2", "", "", "F11", "", "", "", "", ""};',
            '{"F1", "F5", "F8", "F2", "", "", "", "F11", "", "", "", "", ""};')
    replace(menu, '    case Command::fullscreen: {', '''    case Command::upscale_hud: {
        const char *hint = v.upscale_hud_next && v.scale_next <= 1 ? "  Enhanced+"
            : v.upscale_hud_next != v.upscale_hud_now ? "  restart" : "";
        return std::string("Upscale HUD: < ") + (v.upscale_hud_next ? "On" : "Off") + " >" + hint;
    }
    case Command::fullscreen: {''')
    replace(menu, 'c == Command::sharp_2d || c == Command::fullscreen',
            'c == Command::sharp_2d || c == Command::upscale_hud || c == Command::fullscreen')

    replace(window, 'bool g_sharp_locked = false;', 'bool g_sharp_locked = false;\nbool g_hud_upscale_now = false;')
    replace(window, '        v.sharp_locked = g_sharp_locked;', '''        v.sharp_locked = g_sharp_locked;
        v.upscale_hud_now = g_hud_upscale_now;
        v.upscale_hud_next = g_keys.upscale_hud;''')
    replace(window, '    case Command::sharp_2d:', '''    case Command::upscale_hud:
        g_keys.upscale_hud = !g_keys.upscale_hud;
        rewrite_keys_file([](const std::string &t) { return keymap::with_upscale_hud(t, g_keys.upscale_hud); }, "HUD upscaling");
        set_notice(g_keys.upscale_hud && g_scale_next <= 1 ? "HUD upscaling needs Enhanced resolution or higher"
            : "HUD upscaling applies on restart");
        break;
    case Command::sharp_2d:''')
    replace(window, '    load_keys();\n    // The inner resolution:', '''    load_keys();
    g_hud_upscale_now = g_keys.upscale_hud;
    ps2::os::set_env("PS2_HUD_UPSCALE", g_hud_upscale_now ? "1" : "0");
    // The inner resolution:''')

    replace(gpu, '    const std::uint32_t sharp = g_sharp_2d;', '''    const std::uint32_t sharp = g_sharp_2d;
    const bool has_hud_upscale = shader_text.empty() || shader_text.find("override HUD_UPSCALE") != std::string::npos;
    const bool hud_upscale = scale > 1 && os::env("PS2_HUD_UPSCALE") == "1";
    if (has_hud_upscale && hud_upscale) std::fprintf(stderr, "[gpu] HUD upscaling enabled\\n");''')
    replace(gpu, '        WGPUConstantEntry constants[5];', '        WGPUConstantEntry constants[6];')
    replace(gpu, '        set(has_sharp, "SHARP", static_cast<double>(sharp));',
            '        set(has_sharp, "SHARP", static_cast<double>(sharp));\n        set(has_hud_upscale, "HUD_UPSCALE", hud_upscale ? 1.0 : 0.0);')
    replace(shader, 'override SHARP: u32 = 0u;', '''override SHARP: u32 = 0u;
override HUD_UPSCALE: bool = false;
var<private> hud_sprite: bool = false;''')
    replace(shader, '    return clamp((f - 0.5) * f32(SCALE) * 0.5 * f32(SHARP) + 0.5, 0.0, 1.0);',
            '    let strength = select(f32(SHARP), 1.0, hud_sprite);\n    return clamp((f - 0.5) * f32(SCALE) * 0.5 * strength + 0.5, 0.0, 1.0);')
    replace(shader, '    if (sharp_sprite) {', '    if (sharp_sprite || hud_sprite) {')
    replace(shader, '    sharp_sprite = false;', '    sharp_sprite = false;\n    hud_sprite = false;')
    replace(shader, '            sharp_sprite = SHARP != 0u && SCALE > 1u && abs(abs(du) - abs(dx)) <= abs(dx) * 0.02 && abs(abs(dv) - abs(dy)) <= abs(dy) * 0.02;',
            '''            let native_size = abs(abs(du) - abs(dx)) <= abs(dx) * 0.02 && abs(abs(dv) - abs(dy)) <= abs(dy) * 0.02;
            sharp_sprite = SHARP != 0u && SCALE > 1u && native_size;
            // MOJO's HUD uses blended, depth-independent RGBA sprites at native size.
            // Keep their original coverage, but let the upscaled samples see texel edges.
            hud_sprite = HUD_UPSCALE && SCALE > 1u && native_size && s.tpsm == PSMCT32 && !upscaled_source &&
                has(s, F_TME) && has(s, F_FST) && has(s, F_ABE) && has(s, F_TCC) &&
                has(s, F_BILINEAR) && mode(s, 8u, 2u) == 1u && !mip_levels(s);''')
    replace(shader, '            let point = has(s, F_TME) && (!has(s, F_BILINEAR) || (direct && !upscaled_source)) && !mip_levels(s);',
            '            let point = !hud_sprite && has(s, F_TME) && (!has(s, F_BILINEAR) || (direct && !upscaled_source)) && !mip_levels(s);')
