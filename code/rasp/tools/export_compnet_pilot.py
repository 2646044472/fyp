"""Export a reviewed, frozen author CompNet embedding without target-data training.

Weights/source must be supplied explicitly. No implicit download, classifier
retraining, random initialization fallback or production registration occurs.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
import torch


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('weights',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    spec=importlib.util.spec_from_file_location('reviewed_compnet',args.source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    model=module.compnet(600).eval()
    state=torch.load(args.weights,map_location='cpu',weights_only=True)
    model.load_state_dict(state,strict=True)
    torch.set_num_threads(2)
    class Embedding(torch.nn.Module):
        def __init__(self,model):super().__init__();self.model=model
        def forward(self,image):return self.model.getFeatureCode(image)
    embedding=Embedding(model).eval();rng=np.random.default_rng(20261029)
    tests=[rng.normal(size=(1,1,128,128)).astype(np.float32) for _ in range(3)]
    with torch.inference_mode():reference=[embedding(torch.from_numpy(v)).numpy() for v in tests]
    # The learned Gabor parameters are immutable. Materialize each resulting
    # convolution kernel once, preserving the author's mathematical filter.
    for block in (model.cb1,model.cb2,model.cb3):
        g=block.gabor_conv2d
        with torch.inference_mode():kernel=g.genGaborBank(g.kernel_size,g.channel_in,g.channel_out,g.sigma,g.gamma,g.theta,g.f,g.psi)
        conv=torch.nn.Conv2d(g.channel_in,g.channel_out,g.kernel_size,stride=g.stride,padding=g.padding,bias=False)
        conv.weight=torch.nn.Parameter(kernel.clone(),requires_grad=False);block.gabor_conv2d=conv
    with torch.inference_mode():folded=[embedding(torch.from_numpy(v)).numpy() for v in tests]
    assert all(np.array_equal(a,b) for a,b in zip(reference,folded)),'Gabor materialization changed embedding'
    path=args.output/'compnet-tongji.onnx'
    torch.onnx.export(embedding,torch.from_numpy(tests[0]),str(path),opset_version=17,dynamo=False,
        input_names=['image'],output_names=['embedding'])
    import onnxruntime as ort
    session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
    errors=[]
    for values,expected in zip(tests,reference):
        actual=session.run(None,{'image':values})[0]
        assert actual.shape==(1,512) and np.isfinite(actual).all()
        assert np.allclose(actual,expected,atol=1e-4,rtol=1e-4)
        errors.append(float(np.abs(actual-expected).max()))
    metadata=dict(architecture='Author CompNet frozen Tongji600 embedding',
        source='https://github.com/xuliangcs/compnet',training_on_device_data=False,
        classifier_used=False,source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        checkpoint_sha256=hashlib.sha256(args.weights.read_bytes()).hexdigest(),
        onnx_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        input_shape=[1,1,128,128],output_shape=[1,512],parameters=sum(p.numel() for p in model.parameters()),
        preprocessing='PIL grayscale128, /255; standardize positive pixels by mean and sample std(ddof1)+1e-6; zeros retained',
        gabor_materialization_exact=True,export_max_abs_errors=errors,
        limitation='No Pi latency, device accuracy or unknown rejection has been established')
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(json.dumps(metadata),flush=True)


if __name__=='__main__':main()
