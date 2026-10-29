"""Opt-in pretrained embedding early evidence, unchanged v24 fallback.

The additional metric is kept separate from FastCC. Existing pose-confidence
always wins first. No target-data training or identity-specific routing.
"""
import os
import numpy as np
from PIL import Image
from quality_evidence_matcher import QualityEvidenceMatcher
from anchored_matcher import source_quad
from compnet_pilot import CompNetPilot


class CompNetEvidenceMatcher(QualityEvidenceMatcher):
    name='FastCCCompNetEvidence-v25-experimental'
    magic=2801065

    def __init__(self,base,*,model_root=None,encoder=None):
        super().__init__(base)
        path=model_root or os.environ.get('PALM_COMPNET_MODEL_ROOT')
        if encoder is None and not path:
            self.close()
            raise ValueError('Experimental CompNet matcher requires explicit PALM_COMPNET_MODEL_ROOT')
        try:self.encoder=encoder or CompNetPilot(path,threads=1)
        except Exception:
            self.close();raise

    def _embedding(self,native,source):
        raw=self.geometry.getROIimg(native,source_quad(source))
        if raw is None:raise ValueError('CompNet ROI sampling failed')
        return self.encoder.extract(Image.fromarray(raw))

    def prepare_enrollment(self,features):
        prepared=super().prepare_enrollment(features)
        result=[]
        for sample,feature in zip(prepared,features):
            q=self._unpack(feature)
            result.append((*sample,self._embedding(q[3],q[1][2])))
        return result

    def _auxiliary_scores(self,probe,groups):
        keys=[(u,j) for u,ss in groups.items() for j in range(len(ss))]
        if len(groups)<2:return None
        query=self._embedding(probe.native,probe.source)
        gallery=np.asarray([groups[u][j][5] for u,j in keys])
        if gallery.shape!=(len(keys),512):raise ValueError('Invalid prepared CompNet gallery')
        distances=np.arccos(np.clip(gallery@query,-1,1))/np.pi
        pairs=dict(zip(keys,distances))
        return {u:self._aggregate([pairs[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
