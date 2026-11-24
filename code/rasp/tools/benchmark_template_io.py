"""Compare lossless template compression in isolated scratch files on Pi."""
import argparse
import hashlib
import json
import tempfile
import time
import zipfile
from pathlib import Path
import numpy as np
from replay_ready_queries import power_sample,power_fault


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('templates',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    report=dict(records=[],power=[])
    def checkpoint():
        sample=power_sample();report['power'].append(sample)
        args.output.write_text(json.dumps(report,indent=2))
        if power_fault(sample):raise RuntimeError('Power/throttle fault')
    checkpoint()
    for source in sorted(args.templates.glob('*.npz')):
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        with np.load(source,allow_pickle=False) as archive:features=archive['features']
        for repeat,levels in enumerate(((6,1,0),(0,1,6))):
            for level in levels:
                with tempfile.NamedTemporaryFile(dir=args.output.parent,suffix='.npz',delete=False) as stream:
                    path=Path(stream.name)
                try:
                    start=time.perf_counter()
                    if level==6:np.savez_compressed(path,features=features)
                    else:
                        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED if level else zipfile.ZIP_STORED,
                                compresslevel=level if level else None) as archive:
                            with archive.open('features.npy','w',force_zip64=True) as stream:
                                np.lib.format.write_array(stream,features,allow_pickle=False)
                    saved=time.perf_counter()
                    with np.load(path,allow_pickle=False) as archive:restored=archive['features']
                    loaded=time.perf_counter()
                    assert features.dtype==restored.dtype and np.array_equal(features,restored)
                    report['records'].append(dict(template=source.name,repeat=repeat,level=level,
                        save_ms=(saved-start)*1000,load_ms=(loaded-saved)*1000,bytes=path.stat().st_size,exact=True))
                finally:path.unlink(missing_ok=True)
                checkpoint()
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    assert report['records']
    report['originals_unchanged']=True;checkpoint()


if __name__=='__main__':main()
