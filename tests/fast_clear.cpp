// Compile the production eligibility/parameter code with synthetic renderer state.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <vector>
namespace fixture {
constexpr unsigned kPrimWords=28, kSetupWords=40, PSMCT32=0, PSMZ32=48, kKindMask=255, kMemorySize=4u<<20;
enum Pipeline { kFastClear };
struct Range {
    std::uint64_t lo,hi;
    bool overlaps(std::uint64_t a,std::uint64_t z) const { return lo<z && a<hi; }
};
struct Batch {
    std::vector<std::uint32_t> prims, setups;
    unsigned fbp=0,fbw=1,fpsm=0,zbp=128,zpsm=48;
    int minx=0,miny=0,maxx=63,maxy=63;
    bool zwrite=true;
} g_batch;
namespace hwcache { bool g_on=false; }
namespace stat { bool g_on=false; }
bool g_fast_clear=true,g_live=false,g_batch_log=false,reset=false;
struct { bool capturing=false; } g_bench;
std::vector<Range> g_batch_reads,marked;
unsigned g_scale=1,items=0;
std::uint64_t g_fast_clears=0;
std::vector<unsigned> params;
float u2f(unsigned v) { return std::bit_cast<float>(v); }
Range pages(unsigned bp,unsigned bw,unsigned,int,int y0,int,int y1) {
    const auto lo=std::uint64_t(bp)*256+std::uint64_t(y0/32)*bw*8192;
    return {lo,lo+std::uint64_t((y1-y0+1)/32)*bw*8192};
}
unsigned push_params(std::initializer_list<unsigned> p) { params=p;return 0; }
void dispatch_linear(Pipeline,unsigned n,unsigned) { items=n; }
void mark_rendered(Range r) { marked.push_back(r); }
void reset_batch() { reset=true; }
#include "fast_clear.inc"
void check(bool b) { if(!b) std::abort(); }
void init() {
    g_batch=Batch{};g_batch.prims.assign(28,0);g_batch.setups.assign(40,0);
    auto &p=g_batch.prims;auto &w=g_batch.setups;
    p[1]=1;p[6]=std::bit_cast<unsigned>(64.0f);p[7]=p[6];p[13]=0x80123456;p[24]=123456;
    w[0]=512|2048;w[2]=1;w[5]=128;w[6]=48;w[7]=1<<8;w[10]=63<<16;w[11]=63<<16;w[23]=~0u;
    params.clear();marked.clear();items=0;reset=false;
    g_fast_clear=true;g_live=false;hwcache::g_on=false;stat::g_on=false;
    g_batch_log=false;g_bench.capturing=false;g_batch_reads.clear();
}
}
int main() {
    using namespace fixture;
    unsigned cases=0;
    for(unsigned scale=1;scale<=4;++scale) for(unsigned mask:{0u,~0u,0x00ffffffu,0xff000000u,0x55555555u})
        for(unsigned alpha:{0u,1u,127u,128u,255u}) for(bool fba:{false,true}) for(bool zmask:{false,true}) {
            init();g_scale=scale;g_batch.setups[4]=mask;
            g_batch.setups[0]|=(fba?4096u:0u)|(zmask?32u:0u);
            g_batch.prims[13]=(alpha<<24)|0x123456;
            check(try_fast_clear() && reset && params.size()==7);
            check(params[0]==0 && params[1]==4096*scale*scale);
            check(params[2]==(((alpha|(fba?128u:0u))<<24)|0x123456));
            check(params[3]==mask && params[4]==8192*scale*scale);
            check(params[5]==(zmask?0u:4096*scale*scale) && params[6]==123456);
            for(unsigned old:{0u,~0u,0xdeadbeefu}) {
                unsigned actual=(old&params[3])|(params[2]&~params[3]);
                for(unsigned bit=0;bit<32;++bit) check(((actual>>bit)&1)==(((mask>>bit)&1)?((old>>bit)&1):((params[2]>>bit)&1)));
            }
            ++cases;
        }
    // Independent exhaustive proof of the sole accepted blend equation.
    for(int src=0;src<256;++src) for(int dst=0;dst<256;++dst) check((((src-dst)*128)>>7)+dst==src);
    init();g_batch.setups[0]|=8;g_batch.setups[7]|=(1<<14)|(1<<18);check(try_fast_clear());++cases;
    for(unsigned scenario=0;scenario<32;++scenario) {
        init();auto &b=g_batch;auto &w=b.setups;auto &p=b.prims;
        switch(scenario) {
        case 0:w[0]|=2;break;case 1:w[0]|=4;break;case 2:w[0]|=128;break;
        case 3:w[7]|=2u<<28;break;case 4:w[0]|=64;break;case 5:w[7]=2<<8;break;
        case 6:w[7]=3<<8;break;case 7:b.fpsm=2;break;case 8:b.zpsm=50;break;
        case 9:b.maxx=62;break;case 10:b.maxy=62;break;case 11:p[4]=std::bit_cast<unsigned>(0.5f);break;
        case 12:p[6]=std::bit_cast<unsigned>(-64.0f);break;case 13:w[10]=62<<16;break;
        case 14:w[11]=62<<16;break;case 15:b.zbp=w[5]=0;break;case 16:b.fbp=w[1]=16383;break;
        case 17:p[0]=~0u;break;case 18:p[1]=0;break;case 19:w[0]|=8;break;
        case 20:b.minx=1;break;case 21:b.miny=1;break;case 22:b.fbw=0;break;
        case 23:w[3]=1;break;case 24:p.push_back(0);break;
        case 25:g_fast_clear=false;break;case 26:g_live=true;break;
        case 27:hwcache::g_on=true;break;case 28:fixture::stat::g_on=true;break;
        case 29:g_batch_log=true;break;case 30:g_bench.capturing=true;break;
        case 31:g_batch_reads.push_back({0,1});break;
        }
        check(!try_fast_clear() && !reset && params.empty());++cases;
    }
    std::printf("PASS: %u clear parameter/guard cases and 65536 exact blend identities\n",cases);
}
