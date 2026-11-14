// Optional real-GPU differential fixture. No game or game data is used.
// Run twice with PS2_FAST_CLEAR=0/1 and compare stdout, independently at each scale.
#include "gs/gpu/gpu.hpp"
#include "gs/gs.hpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
using namespace ps2::gs;
int main() {
    ps2::gs::init();
    if (gpu::mode()!=gpu::Mode::primary) return 2;
    unsigned scale=1;
    std::vector<std::uint32_t> initial,clut;
    gpu::read_state(initial,scale,clut);
    std::uint32_t rng=0x491879;
    for(auto &v:initial) { rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;v=rng; }
    for(unsigned row=0;row<24;++row) {
        gpu::write_state(initial,scale,clut);
        State s{};auto &c=s.ctx[0];
        const unsigned mask[]={0u,0x00ffffffu,0xff000000u};
        c.frame=(1ull<<16)|(std::uint64_t(mask[row%3])<<32);
        c.zbuf=4ull|((row&2)?1ull<<32:0);
        c.scissor=(63ull<<16)|(63ull<<48);
        c.test=(1ull<<16)|(1ull<<17)|((row&4)?3ull:0ull);
        c.alpha=(1ull<<2)|(1ull<<6);
        c.fba=row&1;
        s.prim=6ull|((row&8)?1ull<<6:0ull);
        s.prmodecont=1;s.colclamp=1;
        Vertex v[2]{};v[0].q=v[1].q=1;
        v[1].x=64*16;v[1].y=64*16;
        v[1].r=31;v[1].g=187;v[1].b=245;v[1].a=(row&8)?128:77;
        v[1].z=0x12345678;
        switch(row) {
        case 12:v[0].x=8;break;
        case 13:v[1].x=32*16;break;
        case 14:c.scissor=(31ull<<16)|(63ull<<48);break;
        case 15:c.test|=1;c.test&=~(7ull<<1);break;
        case 16:c.test|=1ull<<14;break;
        case 17:s.scanmsk=2;break;
        case 18:c.frame|=1ull<<24;break;
        case 19:c.frame|=2ull<<24;break;
        case 20:c.zbuf|=1ull<<24;break;
        case 21:std::swap(v[0].x,v[1].x);break;
        case 22:v[1].y=33*16;break;
        case 23:v[0].y=32*16;break;
        }
        ++g_setup_generation;
        gpu::draw(s,v,2);
        gpu::flush();gpu::wait_idle();
        std::vector<std::uint32_t> after,palette;unsigned n=0;
        gpu::read_state(after,n,palette);
        std::uint64_t hash=14695981039346656037ull;
        for(auto word:after) for(unsigned shift=0;shift<32;shift+=8) {
            hash^=(word>>shift)&255;hash*=1099511628211ull;
        }
        std::printf("%u %u %016llx\n",scale,row,static_cast<unsigned long long>(hash));
    }
    gpu::stats();
}
