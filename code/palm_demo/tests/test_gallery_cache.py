import numpy as np
from gallery import Gallery
from templates import TemplateStore


class PreparedDistance:
    def __init__(self):self.enroll_calls=0;self.probe_calls=0
    def prepare_probe(self,p):self.probe_calls+=1;return p
    def prepare_enrollment(self,f):self.enroll_calls+=1;return f.copy()
    def prepared_bytes(self,f):return f.nbytes
    def score_prepared(self,p,f):return float(np.min(np.abs(f-p)))


def test_cache_reuses_templates_but_invalidates_reenrollment_and_deletion(tmp_path):
    s=TemplateStore(tmp_path);a=PreparedDistance();g=Gallery(s,a,threshold=1)
    s.save('a',np.array([[.1]]),{'capture_profile':'rgb'})
    s.save('b',np.array([[.8]]),{'capture_profile':'rgb'})
    assert g.identify(np.array([.1])).user_id=='a'
    assert g.identify(np.array([.1])).user_id=='a'
    assert (a.enroll_calls,a.probe_calls)==(2,2)
    s.save('a',np.array([[.9]]),{'capture_profile':'rgb'})
    assert g.identify(np.array([.1])).user_id=='b'
    assert a.enroll_calls==3
    s.delete('b');assert g.identify(np.array([.1])).user_id=='a'
    assert 'b' not in g._prepared_cache


def test_cache_respects_metadata_change_and_memory_limit(tmp_path):
    s=TemplateStore(tmp_path);a=PreparedDistance();g=Gallery(s,a,threshold=1,required_metadata={'algorithm':'new'})
    s.save('a',np.array([[.1]]),{'capture_profile':'rgb','algorithm':'new'})
    assert g.identify(np.array([.1])).status=='MATCH'
    s.save('a',np.array([[.1]]),{'capture_profile':'rgb','algorithm':'old'})
    assert g.identify(np.array([.1])).reason=='INCOMPATIBLE_TEMPLATES'
    assert a.enroll_calls==1
    s.save('a',np.array([[.1]]),{'capture_profile':'rgb','algorithm':'new'})
    g.prepared_cache_limit_bytes=1
    g.identify(np.array([.1]));g.identify(np.array([.1]))
    assert g._prepared_cache_bytes==0 and a.enroll_calls==3
