#include "keymap.hpp"
#include "quickmenu.hpp"
#include <cassert>
#include <string>
#include <vector>

int main() {
    for (int x=0; x<256; ++x) assert(keymap::camera_x(x,false)==x);
    assert(keymap::camera_x(128,true)==128);
    assert(keymap::camera_x(0,true)==255);
    assert(keymap::camera_x(255,true)==0);
    assert(keymap::camera_x(64,true)==191);
    assert(keymap::camera_x(191,true)==64);
    const std::string initial="# keep player settings\nscale = 3\nmouse_invert = y\nright_stick_invert_x = off\n";
    const auto enabled=keymap::with_right_stick_invert_x(initial,true);
    assert(enabled.find("scale = 3")!=std::string::npos);
    assert(enabled.find("mouse_invert = y")!=std::string::npos);
    assert(enabled.find("# keep player settings")!=std::string::npos);
    auto c=keymap::defaults(); std::vector<std::string> problems;
    keymap::parse(enabled,c,problems);
    assert(problems.empty() && c.right_stick_invert_x && c.mouse_invert==2 && c.scale==3);
    keymap::parse(keymap::with_right_stick_invert_x(enabled,false),c,problems);
    assert(problems.empty() && !c.right_stick_invert_x);
    for (bool x : {false,true}) for (bool y : {false,true}) {
        const auto text=keymap::with_right_stick_invert_y(keymap::with_right_stick_invert_x(initial,x),y);
        auto restored=keymap::defaults();
        keymap::parse(text,restored,problems);
        assert(problems.empty() && restored.right_stick_invert_x==x && restored.right_stick_invert_y==y);
        assert(restored.mouse_invert==2 && restored.scale==3);
    }
    quickmenu::Menu menu; menu.open();
    for (int n=0; n<6; ++n) menu.move(1);
    assert(menu.side()==quickmenu::Command::upscale_hud);
    assert(menu.choose()==quickmenu::Command::upscale_hud);
    assert(!keymap::defaults().upscale_hud);
    const auto hud_text = keymap::with_upscale_hud(enabled, true);
    auto hud_config = keymap::defaults();
    keymap::parse(hud_text, hud_config, problems);
    assert(problems.empty() && hud_config.upscale_hud && hud_config.right_stick_invert_x);
    assert(hud_config.scale==3 && hud_config.mouse_invert==2);
    keymap::parse(keymap::with_upscale_hud(hud_text, false), hud_config, problems);
    assert(problems.empty() && !hud_config.upscale_hud);
    menu.move(2);
    assert(menu.side()==quickmenu::Command::invert_camera_x);
    assert(menu.choose()==quickmenu::Command::invert_camera_x);
    menu.move(1);
    assert(menu.side()==quickmenu::Command::invert_camera_y);
    assert(menu.choose()==quickmenu::Command::invert_camera_y);
}
