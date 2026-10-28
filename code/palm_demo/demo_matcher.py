"""Same guarded scoring as v5, with explicit enrollment-only extraction."""
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from anchored_matcher import FastCCAnchoredUnionMatcher
from pklnet_roi import normalize_roi
from registered_matcher import local_features


class FastCCDemoMatcher(FastCCAnchoredUnionMatcher):
    name='FastCCDemo-v6'
    magic=FastCCAnchoredUnionMatcher.magic+1
    allow_gallery_only=True

    def __init__(self,base,*,workers=2):
        super().__init__(base)
        if workers not in (1,2):raise ValueError('Demo workers must be 1 or 2')
        self.workers=workers
        self._workers=ThreadPoolExecutor(max_workers=workers,thread_name_prefix='palm-demo')

    def close(self):
        self._workers.shutdown(wait=True,cancel_futures=True)

    def _all_hypothesis_views(self,gray,image_size,hypotheses):
        groups=self._workers.map(lambda h:self._hypothesis_views(gray,image_size,h),hypotheses)
        return [view for group in groups for view in group]

    def score_prepared(self,probe,enrolled):
        if not enrolled:raise ValueError('At least one enrollment feature is required')
        scores=self._workers.map(lambda f:self._match_unpacked(probe,f),enrolled)
        return float(np.mean(sorted(scores)[:2]))

    def extract_gallery_with_context(self,full,quad,normalized_roi):
        legacy=self.legacy.extract_with_context(full,quad,normalized_roi)
        primary,_=self.legacy._views(legacy)
        pixels=normalize_roi(primary[1][192:576,192:576])[0];gallery=[]
        for sigma in [4,8]:
            p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma))
            gallery.append(self._encode_view(sigma,np.eye(3),p,d))
        return self._pack(legacy,np.empty(0,np.uint8),[],gallery)

    def prepare_probe(self,probe):
        parts=super().prepare_probe(probe)
        if parts[4] and not parts[5]:raise ValueError('Enrollment-only template cannot be used as a probe')
        return parts

    def match(self,probe,candidate):
        return self._match_unpacked(self.prepare_probe(probe),self._unpack(candidate,decode_native=False))

    def score_enrollment(self,probe,enrolled):
        return self.score_prepared(self.prepare_probe(probe),self.prepare_enrollment(enrolled))
