"""Export one reviewed frozen author PPNet checkpoint; no fitting or downloads."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
import torch


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('checkpoint',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    args.output.mkdir(exist_ok=False,parents=True)
    spec=importlib.util.spec_from_file_location('reviewed_author_ppnet',args.source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    model=module.ppnet(600).eval()
    model.load_state_dict(torch.load(args.checkpoint,map_location='cpu',weights_only=True),strict=True)
    torch.set_num_threads(2)
    class Embedding(torch.nn.Module):
        def __init__(self,model):super().__init__();self.model=model
        def forward(self,image):
            raw=self.model.getFeatureCode(image)
            return raw,torch.nn.functional.normalize(raw,p=2,dim=1)
    embedding=Embedding(model).eval();rng=np.random.default_rng(20261030)
    tests=[rng.normal(size=(1,1,128,128)).astype(np.float32) for _ in range(3)]
    with torch.inference_mode():reference=[tuple(v.numpy() for v in embedding(torch.from_numpy(x))) for x in tests]
    path=args.output/'ppnet-tongji.onnx'
    torch.onnx.export(embedding,torch.from_numpy(tests[0]),str(path),opset_version=17,dynamo=False,
        input_names=['image'],output_names=['raw_embedding','embedding'])
    import onnxruntime as ort
    session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider']);errors=[]
    for values,expected in zip(tests,reference):
        actual=session.run(None,{'image':values})
        assert all(v.shape==(1,512) and np.isfinite(v).all() for v in actual)
        assert np.allclose(actual[0],expected[0],atol=1e-4,rtol=1e-4)
        normalized_error=float(np.abs(actual[1]-expected[1]).max());assert normalized_error<=1e-5
        errors.append(dict(raw_max_abs=float(np.abs(actual[0]-expected[0]).max()),normalized_max_abs=normalized_error))
    metadata=dict(architecture='Author frozen PPNet Tongji600 features; classifier unused',
        source='https://github.com/xuliangcs/ppnet',checkpoint_file_id='1cjG7ZshKBbkzWzoCLyliqbjQZsIWNt97',
        source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
        onnx_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),parameters=sum(p.numel() for p in model.parameters()),
        training_on_device_data=False,classifier_used=False,input_shape=[1,1,128,128],output_dimension=512,
        preprocessing='Author gray128 /255, positive-pixel mean/sample std+1e-6; zeros kept',
        metrics='Author raw feature Euclidean ranking control; experimental L2 angular confidence control, not calibrated FAR',
        export_parity=errors)
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata),flush=True)


if __name__=='__main__':main()
