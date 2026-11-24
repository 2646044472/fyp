import math
from ranked_window import Candidate, Window, select_set

def c(i,t,sharp=.72,contrast=5,cx=.50,deg=0,scale=.33,tex=(0,.3,.5,.2,.8,1)):
    return Candidate(i,t,sharp,contrast,cx,.5,scale,math.radians(deg),tex)
def ids(items):return [x.frame_id for x in items]

# Five weak but plausible camera frames finish without waiting for absolute sharpness 2.
w=Window(10)
for i in range(5):
    status, selected=w.observe(c(i+1,10+i*.34,cx=.47+.02*i,deg=5*i),10.02+i*.34)
assert status=="ready" and len(selected)==5 and w.status(11.38)[0]=="ready"
# A very sharp mis-crop cannot become the anchor of a supported group.
natural=[c(i+1,i*.34,cx=.47+.02*i,deg=5*i) for i in range(5)]
outlier=c(99,2.5,sharp=99,cx=.95,deg=78,scale=.13)
assert set(ids(select_set(natural+[outlier])))==set(range(1,6))
# Frames within 240ms or essentially identical image+geometry do not pad the set.
near=[c(1,1),c(2,1.1,deg=8),c(3,1.7,cx=.501,deg=.8),c(4,2.1,deg=9)]
assert len(select_set(near))==2
# Hard stop includes no-hand period; no frame arriving at/after cutoff is consumed.
w=Window(0)
assert w.status(19.9)[0]=="collecting"
assert w.observe(c(1,20),20)==("partial",())
# Preserve provisional photos; refill distinct new captures, not old frame IDs.
w=Window(100)
for i in range(4):
    w.observe(c(1+i,100+.5*i,cx=.46+.025*i,deg=5*i),100.01+.5*i)
assert w.status(108.009)[0]=="collecting"
state, keep=w.status(108.02)
assert state=="partial" and len(keep)==4
follow=w.fill_missing(109)
assert ids(follow.observe(c(4,110,deg=19),110.1)[1])==ids(keep)
state, filled=follow.observe(c(5,110.2,cx=.58,deg=19),110.3)
assert state=="ready" and ids(filled)==ids(keep)+[5]
for timeout in [120.1,0,float("nan")]:
    try:
        Window(0,absolute_timeout_s=timeout)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid timeout was accepted")
print("PASS: bounded/no-frame, early finish, useful diversity, relative quality, stale/duplicate guard, partial fill")
