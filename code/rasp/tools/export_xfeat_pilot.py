"""Export reviewed upstream XFeat backbone for an isolated fixed-shape pilot."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
import torch


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    sys.path.insert(0,str(args.upstream.resolve()))
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from modules.model import XFeatModel
    model=XFeatModel().eval()
    model.load_state_dict(torch.load(args.upstream/'weights/xfeat.pt',map_location='cpu',weights_only=True))
    torch.set_num_threads(2)
    import onnxruntime as ort
    from xfeat_alignment_pilot import decode_sparse
    from modules.xfeat import XFeat
    reference=XFeat(weights=None,top_k=1000);reference.net=model
    metadata=dict(source='https://github.com/verlab/accelerated_features',license='Apache-2.0',
        weights_sha256=hashlib.sha256((args.upstream/'weights/xfeat.pt').read_bytes()).hexdigest(),
        source_sha256={str(f.relative_to(args.upstream)):hashlib.sha256(f.read_bytes()).hexdigest()
            for f in (args.upstream/'modules').glob('*.py')},models={},parity=[])
    rng=np.random.default_rng(20261029)
    for side in (384,768):
        path=args.output/f'xfeat-{side}.onnx'
        tensor=torch.from_numpy(rng.random((1,1,side,side),dtype=np.float32))
        with torch.inference_mode():expected=[t.numpy() for t in model(tensor)]
        torch.onnx.export(model,tensor,str(path),opset_version=17,dynamo=False,
            input_names=['image'],output_names=['features','logits','reliability'])
        session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
        actual=session.run(None,{'image':tensor.numpy()})
        error=[float(np.max(np.abs(a-b))) for a,b in zip(expected,actual)]
        assert all(np.allclose(a,b,atol=1e-4,rtol=1e-4) for a,b in zip(expected,actual)),error
        metadata['models'][str(side)]=hashlib.sha256(path.read_bytes()).hexdigest()
        metadata['parity'].append(dict(side=side,maximum_absolute_errors=error))
        ref=reference.detectAndCompute(tensor)[0]
        points,descriptors=decode_sparse(*expected,side)
        rp=ref['keypoints'].cpu().numpy();rd=ref['descriptors'].cpu().numpy()
        assert np.array_equal(points,rp),(side,'sparse point mismatch',len(points),len(rp))
        assert np.allclose(descriptors,rd,atol=1e-4,rtol=1e-4),float(np.max(np.abs(descriptors-rd)))
        metadata['parity'][-1]['sparse_decoder_max_error']=float(np.max(np.abs(descriptors-rd)))
        print(side,error,flush=True)
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')


if __name__=='__main__':main()
