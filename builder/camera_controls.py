"""Independent host-side right-stick X/Y inversion; left stick is unchanged."""
import importlib.util
from pathlib import Path

def apply(engine):
    if 'bool right_stick_invert_y = false;' in (engine/'host/keymap.hpp').read_text():
        return
    spec = importlib.util.spec_from_file_location('display_labels', Path(__file__).with_name('display_labels.py'))
    labels = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(labels)
    replace = labels.replace_once
    replace(engine/'host/keymap.hpp', '#include <string>', '#include <cstdint>\n#include <string>')
    replace(engine/'host/keymap.hpp', '    int mouse_stick = 0;', '    bool right_stick_invert_x = false;\n    int mouse_stick = 0;')
    replace(engine/'host/keymap.hpp', 'Config defaults();', '''Config defaults();
std::string with_right_stick_invert_x(const std::string &text, bool enabled);
inline std::uint8_t camera_x(std::uint8_t value, bool inverted) {
    return inverted && value != 0x80 ? static_cast<std::uint8_t>(255 - value) : value;
}''')
    replace(engine/'host/keymap.cpp', '        if (name == "mousestick") {', '''        if (name == "rightstickinvertx") {
            const std::string v = squash(value);
            if (v == "on" || v == "true" || v == "1") config.right_stick_invert_x = true;
            else if (v == "off" || v == "false" || v == "0") config.right_stick_invert_x = false;
            else bad("right_stick_invert_x is on or off, ignored");
            continue;
        }
        if (name == "mousestick") {''')
    replace(engine/'host/keymap.cpp', 'std::string with_scale(', '''std::string with_right_stick_invert_x(const std::string &text, bool enabled) {
    return with_line(text, "rightstickinvertx", std::string("right_stick_invert_x = ") + (enabled ? "on" : "off"));
}
std::string with_scale(''')
    replace(engine/'host/quickmenu.hpp', '    none, resume, save, load, look, scale, sharp_2d, fullscreen, keys, quit,',
            '    none, resume, save, load, look, scale, sharp_2d, fullscreen, keys, quit, invert_camera_x,')
    replace(engine/'host/quickmenu.hpp', '    bool fullscreen = false;', '    bool invert_camera_x = false;\n    bool fullscreen = false;')
    replace(engine/'host/quickmenu.cpp', 'constexpr int kEntries = 10;', 'constexpr int kEntries = 11;')
    replace(engine/'host/quickmenu.cpp', 'Command::fullscreen, Command::keys, Command::change_keys, Command::quit};',
            'Command::fullscreen, Command::invert_camera_x, Command::keys, Command::change_keys, Command::quit};')
    replace(engine/'host/quickmenu.cpp', '{"F1", "F5", "F8", "F2", "", "", "F11", "", "", ""};',
            '{"F1", "F5", "F8", "F2", "", "", "F11", "", "", "", ""};')
    replace(engine/'host/quickmenu.cpp', '    case Command::keys: return "Show keys";',
            '    case Command::invert_camera_x: return std::string("Invert right stick X: < ") + (v.invert_camera_x ? "On" : "Off") + " >";\n    case Command::keys: return "Show keys";')
    replace(engine/'host/quickmenu.cpp', 'c == Command::fullscreen ? c : Command::none;',
            'c == Command::fullscreen || c == Command::invert_camera_x ? c : Command::none;')
    replace(engine/'host/window.cpp', '        v.scale_locked = g_scale_locked;',
            '        v.scale_locked = g_scale_locked;\n        v.invert_camera_x = g_keys.right_stick_invert_x;')
    replace(engine/'host/window.cpp', '    if (g_menu.is_open()) g_block_input[port] = true;',
            '    rx = keymap::camera_x(rx, g_keys.right_stick_invert_x);\n    if (g_menu.is_open()) g_block_input[port] = true;')
    replace(engine/'host/window.cpp', '    case Command::fullscreen: toggle_fullscreen(); break;', '''    case Command::invert_camera_x:
        g_keys.right_stick_invert_x = !g_keys.right_stick_invert_x;
        rewrite_keys_file([](const std::string &t) { return keymap::with_right_stick_invert_x(t, g_keys.right_stick_invert_x); }, "right stick X inversion");
        set_notice(std::string("Right stick X inverted: ") + (g_keys.right_stick_invert_x ? "On" : "Off"));
        break;
    case Command::fullscreen: toggle_fullscreen(); break;''')
    replace(engine/'host/keymap.hpp', '    bool right_stick_invert_x = false;',
            '    bool right_stick_invert_x = false;\n    bool right_stick_invert_y = false;')
    replace(engine/'host/keymap.hpp', 'Config defaults();',
            'Config defaults();\nstd::string with_right_stick_invert_y(const std::string &text, bool enabled);')
    replace(engine/'host/keymap.cpp', '        if (name == "mousestick") {', '''        if (name == "rightstickinverty") {
            const std::string v = squash(value);
            if (v == "on" || v == "true" || v == "1") config.right_stick_invert_y = true;
            else if (v == "off" || v == "false" || v == "0") config.right_stick_invert_y = false;
            else bad("right_stick_invert_y is on or off, ignored");
            continue;
        }
        if (name == "mousestick") {''')
    replace(engine/'host/keymap.cpp', 'std::string with_scale(', '''std::string with_right_stick_invert_y(const std::string &text, bool enabled) {
    return with_line(text, "rightstickinverty", std::string("right_stick_invert_y = ") + (enabled ? "on" : "off"));
}
std::string with_scale(''')
    replace(engine/'host/quickmenu.hpp', 'quit, invert_camera_x,', 'quit, invert_camera_x, invert_camera_y,')
    replace(engine/'host/quickmenu.hpp', '    bool invert_camera_x = false;',
            '    bool invert_camera_x = false;\n    bool invert_camera_y = false;')
    replace(engine/'host/quickmenu.cpp', 'constexpr int kEntries = 11;', 'constexpr int kEntries = 12;')
    replace(engine/'host/quickmenu.cpp', 'Command::invert_camera_x, Command::keys,',
            'Command::invert_camera_x, Command::invert_camera_y, Command::keys,')
    replace(engine/'host/quickmenu.cpp', '{"F1", "F5", "F8", "F2", "", "", "F11", "", "", "", ""};',
            '{"F1", "F5", "F8", "F2", "", "", "F11", "", "", "", "", ""};')
    replace(engine/'host/quickmenu.cpp', '    case Command::keys: return "Show keys";',
            '    case Command::invert_camera_y: return std::string("Invert right stick Y: < ") + (v.invert_camera_y ? "On" : "Off") + " >";\n    case Command::keys: return "Show keys";')
    replace(engine/'host/quickmenu.cpp', 'c == Command::invert_camera_x ? c : Command::none;',
            'c == Command::invert_camera_x || c == Command::invert_camera_y ? c : Command::none;')
    replace(engine/'host/window.cpp', '        v.invert_camera_x = g_keys.right_stick_invert_x;',
            '        v.invert_camera_x = g_keys.right_stick_invert_x;\n        v.invert_camera_y = g_keys.right_stick_invert_y;')
    replace(engine/'host/window.cpp', '    rx = keymap::camera_x(rx, g_keys.right_stick_invert_x);',
            '    rx = keymap::camera_x(rx, g_keys.right_stick_invert_x);\n    ry = keymap::camera_x(ry, g_keys.right_stick_invert_y);')
    replace(engine/'host/window.cpp', '    case Command::fullscreen: toggle_fullscreen(); break;', '''    case Command::invert_camera_y:
        g_keys.right_stick_invert_y = !g_keys.right_stick_invert_y;
        rewrite_keys_file([](const std::string &t) { return keymap::with_right_stick_invert_y(t, g_keys.right_stick_invert_y); }, "right stick Y inversion");
        set_notice(std::string("Right stick Y inverted: ") + (g_keys.right_stick_invert_y ? "On" : "Off"));
        break;
    case Command::fullscreen: toggle_fullscreen(); break;''')
