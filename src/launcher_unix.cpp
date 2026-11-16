// Native Linux launcher. No shell interpolation of player-selected paths.
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>
#include <unistd.h>
#include <dlfcn.h>

static std::string pick_disc() {
    void *gtk = dlopen("libgtk-3.so.0", RTLD_NOW | RTLD_LOCAL);
    if (!gtk) return {};
    auto init = reinterpret_cast<int (*)(int *, char ***)>(dlsym(gtk, "gtk_init_check"));
    auto dialog = reinterpret_cast<void *(*)(const char *, void *, int, const char *, ...)>(dlsym(gtk, "gtk_file_chooser_dialog_new"));
    auto run = reinterpret_cast<int (*)(void *)>(dlsym(gtk, "gtk_dialog_run"));
    auto filename = reinterpret_cast<char *(*)(void *)>(dlsym(gtk, "gtk_file_chooser_get_filename"));
    auto destroy = reinterpret_cast<void (*)(void *)>(dlsym(gtk, "gtk_widget_destroy"));
    auto release = reinterpret_cast<void (*)(void *)>(dlsym(gtk, "g_free"));
    if (!init || !dialog || !run || !filename || !destroy || !release || !init(nullptr, nullptr)) return {};
    void *window = dialog("Select your MOJO! USA PS2 ISO, CHD or CUE/BIN", nullptr, 0,
                          "Cancel", -6, "Open", -3, nullptr);
    std::string result;
    if (run(window) == -3) {
        if (char *path = filename(window)) { result = path; release(path); }
    }
    destroy(window);
    // The process is immediately replaced, so no GTK event loop remains in the game.
    return result;
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "MOJO native Linux launcher\n";
        return 0;
    }
    char path[65536];
    auto size = readlink("/proc/self/exe", path, sizeof(path)-1);
    if (size <= 0 || size == sizeof(path)-1) return 21;
    path[size] = 0;
    auto root = std::filesystem::path(path).parent_path();
    std::vector<std::string> args = {"sh", (root/"builder/bootstrap.sh").string(), root.string()};
    bool headless = false, game = false;
    for (int i = 1; i < argc; ++i) {
        args.emplace_back(argv[i]);
        headless |= args.back() == "--prepare";
        game |= args.back() == "--game";
    }
    if (!game && !headless && !std::filesystem::is_regular_file(root/"userdata/disc.iso")) {
        auto disc = pick_disc();
        if (disc.empty()) {
            std::cerr << "No disc selected. A GTK3 desktop is needed for the picker; alternatively use MOJO --game /path/to/disc.cue.\n";
            return 20;
        }
        args.insert(args.end(), {"--game", disc});
    }
    std::vector<char *> pointers;
    for (auto &arg : args) pointers.push_back(arg.data());
    pointers.push_back(nullptr);
    execv("/bin/sh", pointers.data());
    return 21;
}
