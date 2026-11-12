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
    quickmenu::Menu menu; menu.open();
    for(int n=0;n<7;++n) menu.move(1);
    assert(menu.side()==quickmenu::Command::invert_camera_x);
    assert(menu.choose()==quickmenu::Command::invert_camera_x);
}
