#include "host_clock.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <thread>

int main() {
    // Independent wall-clock elapsed time catches a raw-counter frequency
    // mismatch even when counter() and frequency() are mutually consistent.
    const auto wall_start=std::chrono::system_clock::now();
    const auto start=mojo::host_clock::counter();
    std::this_thread::sleep_for(std::chrono::milliseconds(300));
    const auto end=mojo::host_clock::counter();
    const double wall=std::chrono::duration<double>(std::chrono::system_clock::now()-wall_start).count();
    const double host=double(end-start)/mojo::host_clock::frequency();
    if(end<start || wall<=0 || std::abs(host-wall)>std::max(.002,wall*.02)) {
        std::fprintf(stderr,"Host clock disagrees with elapsed wall time: %.6f versus %.6f\n",host,wall);
        return 1;
    }
    std::printf("PASS: monotonic host clock matches elapsed wall time\n");
}
