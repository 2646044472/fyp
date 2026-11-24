// Research-only ARM64 kernel. Compute each squared L2 distance once and retain
// both directions' two nearest neighbours. Python rechecks ambiguous decisions.
#include <arm_neon.h>
#include <omp.h>
#include <vector>
#include <limits>
#include <new>
struct Best {
    float d0=std::numeric_limits<float>::infinity(),d1=d0;
    int i0=-1,i1=-1;
    void add(float d,int i) {
        if(d<d0 || (d==d0 && (i0<0 || i<i0))) {
            d1=d0;i1=i0;d0=d;i0=i;
        } else if(d<d1 || (d==d1 && (i1<0 || i<i1))) {d1=d;i1=i;}
    }
};
static float distance128(const float* a,const float* b,float cutoff) {
    float32x4_t s0=vdupq_n_f32(0),s1=s0,s2=s0,s3=s0;
    for(int k=0;k<128;k+=16) {
        auto d0=vsubq_f32(vld1q_f32(a+k),vld1q_f32(b+k));
        auto d1=vsubq_f32(vld1q_f32(a+k+4),vld1q_f32(b+k+4));
        auto d2=vsubq_f32(vld1q_f32(a+k+8),vld1q_f32(b+k+8));
        auto d3=vsubq_f32(vld1q_f32(a+k+12),vld1q_f32(b+k+12));
        s0=vmlaq_f32(s0,d0,d0);s1=vmlaq_f32(s1,d1,d1);
        s2=vmlaq_f32(s2,d2,d2);s3=vmlaq_f32(s3,d3,d3);
#ifdef PALM_PARTIAL_DISTANCE
        // Positive squared terms make this a lower bound on the final sum.
        // Preserve arithmetic order and ties. Skip only when this pair cannot
        // enter either direction's top two, including thread-local reverse.
        if ((k==16 || k==48 || k==80) &&
            vaddvq_f32(vaddq_f32(vaddq_f32(s0,s1),vaddq_f32(s2,s3)))>cutoff)
            return std::numeric_limits<float>::infinity();
#endif
    }
    return vaddvq_f32(vaddq_f32(vaddq_f32(s0,s1),vaddq_f32(s2,s3)));
}
extern "C" int descriptor_neighbours(const float* a,int n,const float* b,int m,
    int threads,int* fi,float* fd,int* ri,float* rd) {
    if(n<2 || m<2 || n>4096 || m>4096 || threads<1 || threads>4)return -1;
    try {
        std::vector<Best> backwards(threads*m);
        #pragma omp parallel num_threads(threads)
        {
            int t=omp_get_thread_num();
            #pragma omp for schedule(static)
            for(int i=0;i<n;i++) {
                Best forward;
                for(int j=0;j<m;j++) {
                    float cutoff=forward.d1>backwards[t*m+j].d1 ? forward.d1 : backwards[t*m+j].d1;
                    float d=distance128(a+128*i,b+128*j,cutoff);
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
