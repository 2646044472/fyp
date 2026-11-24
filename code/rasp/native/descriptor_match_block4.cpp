// Isolated exact-computation pilot: reuse one query across four candidates.
// Retain each distance's original accumulation and final reduction tree.
// The scalar implementation provides Best, tail handling, and a reference
// symbol. Neither the original source nor its default library is replaced.
#define descriptor_neighbours scalar_descriptor_neighbours
#include "descriptor_match.cpp"
#undef descriptor_neighbours

static inline float32x4_t distance4(const float* a,const float* b) {
    float32x4_t s0=vdupq_n_f32(0),s1=s0,s2=s0,s3=s0,s4=s0,s5=s0,s6=s0,s7=s0;
    float32x4_t s8=s0,s9=s0,s10=s0,s11=s0,s12=s0,s13=s0,s14=s0,s15=s0;
#define STEP(R) {auto d=vsubq_f32(vdupq_n_f32(a[k+R]),vld1q_f32(b+4*(k+R)));s##R=vmlaq_f32(s##R,d,d);}
    for(int k=0;k<128;k+=16) {
        STEP(0) STEP(1) STEP(2) STEP(3) STEP(4) STEP(5) STEP(6) STEP(7)
        STEP(8) STEP(9) STEP(10) STEP(11) STEP(12) STEP(13) STEP(14) STEP(15)
    }
#undef STEP
    auto a0=vaddq_f32(vaddq_f32(s0,s4),vaddq_f32(s8,s12));
    auto a1=vaddq_f32(vaddq_f32(s1,s5),vaddq_f32(s9,s13));
    auto a2=vaddq_f32(vaddq_f32(s2,s6),vaddq_f32(s10,s14));
    auto a3=vaddq_f32(vaddq_f32(s3,s7),vaddq_f32(s11,s15));
    return vaddq_f32(vaddq_f32(a0,a1),vaddq_f32(a2,a3));
}

extern "C" int descriptor_neighbours(const float* a,int n,const float* b,int m,
    int threads,int* fi,float* fd,int* ri,float* rd) {
    if(n<2 || m<2 || n>4096 || m>4096 || threads<1 || threads>4)return -1;
    try {
        const int blocks=m/4;
        std::vector<float> packed(blocks*512);
        for(int block=0;block<blocks;block++)
            for(int k=0;k<128;k++)
                for(int t=0;t<4;t++)packed[block*512+k*4+t]=b[(block*4+t)*128+k];
        std::vector<Best> backwards(threads*m);
        #pragma omp parallel num_threads(threads)
        {
            int t=omp_get_thread_num();
            #pragma omp for schedule(static)
            for(int i=0;i<n;i++) {
                Best forward;
                for(int block=0;block<blocks;block++) {
                    float values[4];vst1q_f32(values,distance4(a+128*i,packed.data()+block*512));
                    for(int lane=0;lane<4;lane++) {
                        int j=block*4+lane;float d=values[lane];
                        forward.add(d,j);backwards[t*m+j].add(d,i);
                    }
                }
                for(int j=blocks*4;j<m;j++) {
                    float d=distance128(a+128*i,b+128*j,std::numeric_limits<float>::infinity());
                    forward.add(d,j);backwards[t*m+j].add(d,i);
                }
                fi[2*i]=forward.i0;fi[2*i+1]=forward.i1;
                fd[2*i]=forward.d0;fd[2*i+1]=forward.d1;
            }
        }
        for(int j=0;j<m;j++) {
            Best best;
            for(int t=0;t<threads;t++) {
                const auto& v=backwards[t*m+j];
                if(v.i0>=0)best.add(v.d0,v.i0);
                if(v.i1>=0)best.add(v.d1,v.i1);
            }
            ri[2*j]=best.i0;ri[2*j+1]=best.i1;
            rd[2*j]=best.d0;rd[2*j+1]=best.d1;
        }
    } catch(const std::bad_alloc&) {return -2;}
    return 0;
}
