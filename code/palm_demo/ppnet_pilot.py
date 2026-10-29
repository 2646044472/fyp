"""Frozen PPNet experiment adapter, absent from production registry."""
import hashlib,json
from pathlib import Path
import numpy as np
from compnet_pilot import preprocess_compnet


class PPNetPilot:
    def __init__(self,root,threads=1):
        import onnxruntime as ort
        root=Path(root);self.metadata=json.loads((root/'metadata.json').read_text())
        path=root/'ppnet-tongji.onnx'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==self.metadata['onnx_sha256']
        options=ort.SessionOptions();options.intra_op_num_threads=threads;options.inter_op_num_threads=1
        self.session=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])

    def extract(self,image):
        raw,unit=self.session.run(['raw_embedding','embedding'],{'image':preprocess_compnet(image)})
        if any(v.shape!=(1,512) or not np.isfinite(v).all() for v in (raw,unit)):
            raise ValueError('Invalid PPNet feature output')
        if not .999<=np.linalg.norm(unit[0])<=1.001:raise ValueError('PPNet unit feature is not normalized')
        return raw[0],unit[0]
