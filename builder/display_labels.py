"""Small host-menu-only patch; no renderer, game logic or save-format changes."""
from pathlib import Path

def replace_once(path, old, new):
    text=path.read_text(encoding='utf-8')
    if new in text: return
    if text.count(old)!=1: raise ValueError('Pinned upstream menu source no longer matches')
    path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')

def apply(engine):
    replace_once(engine/'host/quickmenu.hpp', '    bool fullscreen = false;',
                 '    bool fullscreen = false;\n    int desktop_width = 0, desktop_height = 0;')
    replace_once(engine/'host/window.cpp', '        v.fullscreen = SDL_GetWindowFlags(g_window) & SDL_WINDOW_FULLSCREEN;',
                 '''        v.fullscreen = SDL_GetWindowFlags(g_window) & SDL_WINDOW_FULLSCREEN;
        SDL_DisplayMode desktop{};
        if (SDL_GetDesktopDisplayMode(SDL_GetWindowDisplayIndex(g_window), &desktop) == 0) {
            v.desktop_width = desktop.w;
            v.desktop_height = desktop.h;
        }''')
    replace_once(engine/'host/quickmenu.cpp', '''        const std::string now = std::to_string(v.scale_now) + "x";
        if (v.scale_locked) return "Resolution: " + now + " (set by PS2_SCALE)";
        return "Resolution:  < " + std::to_string(v.scale_next) + "x >" + (v.scale_next != v.scale_now ? "  at the next start" : "");''',
                 '''        const auto detail = [](int scale) {
            static const char *names[] = {"Original", "Enhanced", "High", "Ultra"};
            const int n = std::clamp(scale, 1, 4);
            return std::string(names[n - 1]) + " (" + std::to_string(640 * n) + "x" + std::to_string(448 * n) + ")";
        };
        if (v.scale_locked) return "Gameplay: " + detail(v.scale_now) + " [launcher]";
        return "Gameplay: < " + detail(v.scale_next) + " >" + (v.scale_next != v.scale_now ? " restart" : "");''')
    replace_once(engine/'host/quickmenu.cpp', '    case Command::fullscreen: return std::string("Full screen: ") + (v.fullscreen ? "on" : "off");',
                 '''    case Command::fullscreen: {
        const std::string native = v.desktop_width > 0 ? "Native (" + std::to_string(v.desktop_width) + "x" + std::to_string(v.desktop_height) + ")" : "Native";
        return "Display: < " + (v.fullscreen ? native : "Window | " + native) + " >";
    }''')
