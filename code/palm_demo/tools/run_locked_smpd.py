"""Continue the one full SMPD experiment as soon as preparation/CRC complete.

This is a current-task dependency runner, not a scheduled/recurring task. It
adds dependency/model verification to the already frozen evaluation program.
"""
import argparse,json,subprocess,time
from pathlib import Path
import evaluate_raw_smpd as base


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--model',required=True,type=Path);a=p.parse_args()
    root=a.root.resolve();protocol=json.loads((root/'protocol.json').read_text());base.verify(protocol)
    extra_paths=[base.APP/'tools/retained_evidence_pilot.py',base.APP/'tools/replay_pi_pipeline.py',
        base.APP/'palm_app/common.py',base.APP/'models.py',base.APP/'roi_quality.py',base.APP/'palm_roi.py',
        base.PKLNetROI().root/'roiExtractor.py',a.model/'metadata.json']
    extras={str(path.resolve()):base.source_sha(path)for path in extra_paths}
    path=root/'dependency-lock.json'
    value=dict(source_sha256=extras,launcher_sha256=base.source_sha(__file__),
        tracked_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base.APP.parents[1],text=True).strip(),
        supplementary_scope='Protocol source set plus retained-evidence, decoder/HTTP, geometry and metadata dependencies',
        host_memory_allowances=dict(index_bytes=2*1024**3,prepared_cache_bytes=6*1024**3),
        arithmetic_parameters_changed=False,models_retrained=False,thresholds_changed=False)
    if path.exists():assert json.loads(path.read_text())==value
    else:base.save(path,value)
    while True:
        prep=json.loads((root/'prepared/progress.json').read_text());download=json.loads((root/'SMPD.download.json').read_text())
        if prep['complete']and download['complete']:break
        state=root/'parallel-prepare.json';status=json.loads(state.read_text())if state.exists()else prep
        print('waiting-for-full-preparation',status.get('counts'),flush=True);time.sleep(20)
    base.verify(protocol)
    for file,h in extras.items():assert base.source_sha(file)==h,('Frozen dependency changed',file)
    assert base.sha(a.model/'compnet-tongji.onnx')==protocol['model_sha256']['compnet']
    assert base.sha(base.PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')==protocol['model_sha256']['pklnet']
    assert download['zip_crc_checked']
    print('starting-full-single-gallery-recognition',protocol['query_images'],flush=True)
    base.run(a)


if __name__=='__main__':main()
