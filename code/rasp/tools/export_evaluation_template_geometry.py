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
    p.add_argument('--all-enrolled',action='store_true',help='Export every enrolled transform and original FastCC reference code')
    p.add_argument('--native-registration',type=Path,help='Also export within-enrollment similarity links using this native library')
    p.add_argument('--candidates',action='store_true',help='Also export existing stored query-hypothesis transforms, without rerunning localization')
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=json.loads((args.baseline/'results.json').read_text());protocol=data['protocol']
    algorithm=load_algorithm(app/'vendor/palmprint-recognition-python',protocol['matcher'])
    if args.native_registration:
        from native_registration import enable_native_registration
        assert hashlib.sha256(args.native_registration.read_bytes()).hexdigest()==protocol['native_sha256']
        enable_native_registration(algorithm,args.native_registration,1)
    cases={c['name']:c for c in protocol['cases']};result=dict(records=[],links=[],power_samples=[])
    try:
        for run in data['runs']:
            selected={q['identity'].replace(':','-') for q in run['queries'] if not q['correct']}
            selected.update(q['result'].get('user_id') for q in run['queries'] if not q['correct'])
            for identity,samples in cases[run['case']]['enrollment'].items():
                user=identity.replace(':','-')
                if not args.all_enrolled and user not in selected:continue
                power=power_sample();result['power_samples'].append(power)
                if power_fault(power):raise RuntimeError('Power fault')
                path=args.baseline/run['case']/'runtime/demo_templates'/(user+'.npz')
                before=hashlib.sha256(path.read_bytes()).hexdigest()
                with np.load(path,allow_pickle=False) as archive:
                    features=archive['features'];assert len(features)==5
                    parts=[]
                    for sample,feature in zip(samples,features):
                        q=algorithm._unpack(feature,decode_native=False)
                        parts.append(q)
                        result['records'].append(dict(case=run['case'],identity=identity,sample=sample,
                            source_matrix=q[1][2].tolist(),quad=source_quad(q[1][2]).tolist(),template_sha256=before,
                            reference_code=q[1][0][0].tolist()))
                        if args.candidates:
                            sources={}
                            for sigma,matrix,points,desc in q[5]:
                                key=matrix.tobytes()
                                if key not in sources:sources[key]=dict(source_matrix=matrix.tolist(),quad=source_quad(matrix).tolist(),sigmas=[])
                                if sigma not in sources[key]['sigmas']:sources[key]['sigmas'].append(sigma)
                            result['records'][-1]['candidates']=list(sources.values())
                    if args.native_registration:
                        for i,left in enumerate(parts):
                            for j,right in enumerate(parts):
                                if i==j:continue
                                for a,b in (((left[1][4],left[1][5]),(right[1][4],right[1][5])),(left[2],right[2])):
                                    matrix=algorithm.registration(a,b)
                                    if matrix is not None:result['links'].append(dict(case=run['case'],identity=identity,
                                        source=samples[i],target=samples[j],matrix=matrix.tolist()))
                assert hashlib.sha256(path.read_bytes()).hexdigest()==before
                power=power_sample();result['power_samples'].append(power)
                if power_fault(power):raise RuntimeError('Power fault')
        args.output.write_text(json.dumps(result,indent=2))
        print('saved enrollment geometry',len(result['records']))
    finally:algorithm.close()


if __name__=='__main__':main()
