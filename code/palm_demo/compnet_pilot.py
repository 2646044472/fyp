"""Frozen CompNet embedding adapter, isolated from the application registry."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image


def preprocess_compnet(image):
    pixels=np.asarray(image.convert('L').resize((128,128),Image.Resampling.BILINEAR),np.float32)/255
    mask=pixels>0;values=pixels[mask]
    if len(values)<2:raise ValueError('ROI has fewer than two nonzero pixels')
    pixels[mask]=(values-values.mean())/(values.std(ddof=1)+np.float32(1e-6))
    if not np.isfinite(pixels).all():raise ValueError('Nonfinite standardized ROI')
    return pixels[None,None]


class CompNetPilot:
    def __init__(self,root,threads=1):
        import onnxruntime as ort
        root=Path(root);self.metadata=json.loads((root/'metadata.json').read_text())
        path=root/'compnet-tongji.onnx'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==self.metadata['onnx_sha256']
        options=ort.SessionOptions();options.intra_op_num_threads=threads;options.inter_op_num_threads=1
        self.session=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])

    def extract(self,image):
        values=self.session.run(['embedding'],{'image':preprocess_compnet(image)})[0]
        if values.shape!=(1,512) or not np.isfinite(values).all():raise ValueError('Invalid CompNet embedding')
        norm=np.linalg.norm(values[0])
        if not .999<=norm<=1.001:raise ValueError('CompNet embedding is not L2-normalized')
        return values[0]
