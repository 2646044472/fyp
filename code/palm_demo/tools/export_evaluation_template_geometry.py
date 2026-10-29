"""Read saved enrollment geometry for all true/predicted identities in errors."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
app=Path(__file__).resolve().parents[1];sys.path.insert(0,str(app))
from biometric import load_algorithm
from anchored_matcher import source_quad
from replay_ready_queries import power_sample,power_fault


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=json.loads((args.baseline/'results.json').read_text());protocol=data['protocol']
    algorithm=load_algorithm(app/'vendor/palmprint-recognition-python',protocol['matcher'])
    cases={c['name']:c for c in protocol['cases']};result=dict(records=[],power_samples=[])
    try:
        for run in data['runs']:
            selected={q['identity'].replace(':','-') for q in run['queries'] if not q['correct']}
            selected.update(q['result'].get('user_id') for q in run['queries'] if not q['correct'])
            for identity,samples in cases[run['case']]['enrollment'].items():
                user=identity.replace(':','-')
                if user not in selected:continue
                power=power_sample();result['power_samples'].append(power)
                if power_fault(power):raise RuntimeError('Power fault')
                path=args.baseline/run['case']/'runtime/demo_templates'/(user+'.npz')
                before=hashlib.sha256(path.read_bytes()).hexdigest()
                with np.load(path,allow_pickle=False) as archive:
                    features=archive['features'];assert len(features)==5
                    for sample,feature in zip(samples,features):
                        q=algorithm._unpack(feature,decode_native=False)
                        result['records'].append(dict(case=run['case'],identity=identity,sample=sample,
                            source_matrix=q[1][2].tolist(),quad=source_quad(q[1][2]).tolist(),template_sha256=before))
                assert hashlib.sha256(path.read_bytes()).hexdigest()==before
        args.output.write_text(json.dumps(result,indent=2))
        print('saved enrollment geometry',len(result['records']))
    finally:algorithm.close()


if __name__=='__main__':main()
