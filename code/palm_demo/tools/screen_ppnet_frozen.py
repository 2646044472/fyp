"""Predeclared frozen PPNet screen, all current/development queries retained."""
import argparse,hashlib,html,io,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from ppnet_pilot import PPNetPilot
from compnet_context_pilot import confident_identity


def write_report(result,path):
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>冻结 PPNet：最小筛查</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #ccd5df;text-align:left}th{background:#eaf0f7}.notice{background:#fff3dd;border-left:4px solid #a86a16;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>冻结作者 PPNet：一次共享向量能否替代完整回退？</h1><p>2026-10-30 · 先声明淘汰标准，再做离线最小实验 · 无训练或部署</p>'''
    text+='<p class="notice">'+('筛查通过，尚未进行Pi验收。' if result['screen_passed'] else '未通过：'+html.escape(', '.join(result['kill_reasons'])))+' 当前正式算法及完整Pi结果不变：164/168正确、146/168正确且≤2.5秒，P95 6.019秒、最大15.225秒。</p>'
    text+='<p>与CompNet不同的卷积表征，从每张原始主ROI提取一次512维特征，再共享给整个图库，目标是跳过多窗口定位/SIFT/逐模板配准。只测试作者Tongji600公开权重，不在设备图或公开评估集训练，不换标签、不删除失败、不按人员/文件特调。使用全部169活动原图、四个设备内注册方向；历史删图前队列另存。</p>'
    text+='<h2>筛查结果（不是完整识别器或Pi速度）</h2>'+table(['数据','查询数','原特征欧氏排名正确','单位角距离排名正确','固定门槛高置信','其中错误','当前完整回退获救'],[
        [name,s['total'],s['raw_ranking_correct'],s['angular_ranking_correct'],s['confident'],s['wrong_confident'],s['current_exhaustive_correct_confident']] for name,s in result['summary'].items()])
    text+='<p>作者示例用未归一化特征的欧氏距离。单位向量角距离是预先声明的实验控制，仍要求≤0.32且领先≥0.08；这些相同数字不意味着不同表征的FAR已校准。所有4480次历史划分均为已曝光相关回归证据，没有独立泛化声明。</p>'
    records=[t for r in result['results'] if r['cohort']=='active169' for t in r['trials'] if t.get('v26_route')=='exhaustive_fallback']
    rows=[]
    for t in records:
        ranking=sorted(t['scores']['angular'].items(),key=lambda p:p[1]);a,b=ranking[:2]
        rows.append([t['sample'],t['identity'],a[0],t['angular_correct'],f'{a[1]:.6f}',f'{b[1]:.6f}',f'{b[1]-a[1]:.6f}',t['confident']])
    text+='<h2>全部13次完整回退逐条保留</h2>'+table(['样本','真实身份','角距离第一名','排名正确','最佳','第二名','差值','高置信'],rows)
    text+='<p>最难图可以排名第一，但领先幅度仍不足；不把排名对冒充可靠提前接受。不能为它把0.08改小。现有数据没有未注册人员试验；陌生人FAR和验证FRR仍未测，也不宣称零错误高置信就是零FAR。</p>'
    meta=result['protocol']['model']
    text+='<h2>模型与导出检查</h2><p>作者权重安全加载（weights_only=True、完整strict state匹配），分类头不参与推理。原图128灰度，非黑像素用作者均值/样本标准差标准化。模型约'+f"{meta['parameters']/1e6:.2f}"+'M参数（含未用分类头统计），无随机特征层兜底。</p>'
    text+=table(['导出样本','原特征最大绝对误差','单位向量最大绝对误差'],[[i,e['raw_max_abs'],e['normalized_max_abs']] for i,e in enumerate(meta['export_parity'])])
    text+=table(['文件','SHA256'],[[name,meta[key]] for name,key in [('作者源码','source_sha256'),('作者checkpoint','checkpoint_sha256'),('ONNX','onnx_sha256')]])
    text+='<h2>停止条件与实际状态</h2><p>事先规定出现错误高置信，或不能新增覆盖至少一次当前完整回退，就不跑完整Pi。当前触发后者，停止此固定组合；不搜索另一个权重/预处理或放宽门槛来救已曝光图片。没有更换运行中的识别模型，没有PPNet的Pi首轮/热态、HTTP、注册或就绪耗时；本机离线耗时不当作Pi时延。</p>'
    text+='<p>所有权重和作者代码留在忽略目录，不随Git分发；没有上传原始生物图像。<a href="https://github.com/xuliangcs/ppnet">作者实现</a> · <a href="../../compnet-v26-pi-20261030/report.html">当前v26完整Pi基线</a>。</p></html>'
    path.write_text(text,encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cohort',type=Path);p.add_argument('geometry',type=Path);p.add_argument('model',type=Path)
    p.add_argument('reference',type=Path);p.add_argument('development',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    rows=json.loads((args.cohort/'manifest.json').read_text());cohort=json.loads((args.cohort/'protocol.json').read_text())
    reference=json.loads(args.reference.read_text());assert reference['complete']
    refs={(r['case'],q['sample']):q for r in reference['runs'] for q in r['queries']}
    quads={r['sample']:np.asarray(r['quad'],np.float32) for r in json.loads(args.geometry.read_text())['records']}
    lookup={r['sample']:i for i,r in enumerate(rows)};truth={r['sample']:r['identity'] for r in rows}
    args.output.mkdir(exist_ok=False,parents=True);cv2.setNumThreads(1);encoder=PPNetPilot(args.model)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',cohort['matcher'])
    protocol=dict(method='Single saved primary ROI; frozen author PPNet Tongji600; original five-frame best2 aggregation',
        controls=['Author raw-feature Euclidean ranking','Experimental unit-vector angular distance, unchanged nominal .32/.08'],
        kill_criteria='Any wrong confident angular result on current/development trials OR no correct confident current exhaustive query; no checkpoint/preprocess tuning',
        model=encoder.metadata,training_on_device_data=False,independent_validation=False,
        timing_scope='Offline original/geometry/feature reuse; not actual Pi HTTP latency',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),APP/'ppnet_pilot.py',args.geometry,args.reference,args.development,args.cohort/'manifest.json']})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    raw=[];unit=[];started=time.perf_counter();repo=APP.parents[1]
    try:
        for row in rows:
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            native=cv2.cvtColor(np.asarray(Image.open(io.BytesIO(value)).convert('RGB')),cv2.COLOR_RGB2GRAY)
            pixels=algorithm.geometry.getROIimg(native,quads[row['sample']])
            a,b=encoder.extract(Image.fromarray(pixels));raw.append(a);unit.append(b)
        raw=np.asarray(raw);unit=np.asarray(unit);a=raw.astype(np.float64);norm=np.sum(a*a,axis=1)
        euclidean=np.sqrt(np.maximum(norm[:,None]+norm[None,:]-2*a@a.T,0))
        angular=np.arccos(np.clip(unit@unit.T,-1,1))/np.pi
        cases=[dict(case=c['name'],gallery=c['enrollment'],trials=[dict(sample=s,identity=truth[s]) for s in c['queries']],cohort='active169') for c in cohort['cases']]
        cases.extend(dict(c,cohort='development') for c in json.loads(args.development.read_text()))
        results=[]
        for case in cases:
            enrolled={u:[lookup[s] for s in ss] for u,ss in case['gallery'].items()};trials=[]
            assert not ({t['sample'] for t in case['trials']}&{s for ss in case['gallery'].values() for s in ss})
            for trial in case['trials']:
                i=lookup[trial['sample']]
                scores={name:{u:float(np.sort(m[i,ids])[:2].mean()) for u,ids in enrolled.items()}
                    for name,m in [('euclidean',euclidean),('angular',angular)]}
                pred={k:min(s,key=s.get) for k,s in scores.items()};confident=confident_identity(scores['angular'])
                t=dict(sample=trial['sample'],identity=trial['identity'],predicted=pred,
                    raw_correct=pred['euclidean']==trial['identity'],angular_correct=pred['angular']==trial['identity'],
                    confident=confident is not None,confident_correct=confident==trial['identity'],scores=scores)
                if case['cohort']=='active169':t['v26_route']=refs[case['case'],trial['sample']]['result']['recognition_route']
                trials.append(t)
            results.append(dict(case=case['case'],cohort=case['cohort'],trials=trials))
        summary={}
        for name in ('active169','development'):
            trials=[t for r in results if r['cohort']==name for t in r['trials']]
            summary[name]=dict(total=len(trials),raw_ranking_correct=sum(t['raw_correct'] for t in trials),
                angular_ranking_correct=sum(t['angular_correct'] for t in trials),confident=sum(t['confident'] for t in trials),
                wrong_confident=sum(t['confident'] and not t['confident_correct'] for t in trials),
                current_exhaustive_correct_confident=sum(t['confident_correct'] and t.get('v26_route')=='exhaustive_fallback' for t in trials))
        reasons=[]
        if any(s['wrong_confident'] for s in summary.values()):reasons.append('Wrong confident angular result')
        if summary['active169']['current_exhaustive_correct_confident']==0:reasons.append('No current exhaustive rescue')
        result=dict(protocol=protocol,summary=summary,results=results,screen_passed=not reasons,kill_reasons=reasons,
            complete=True,elapsed_offline_seconds=time.perf_counter()-started)
        np.savez_compressed(args.output/'features-and-distances.npz',raw=raw,unit=unit,euclidean=euclidean,angular=angular)
        (args.output/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(summary=summary,screen_passed=not reasons,kill_reasons=reasons)),flush=True)
        write_report(result,args.output/'report.html')
    finally:algorithm.close()


if __name__=='__main__':main()
