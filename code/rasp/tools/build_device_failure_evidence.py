"""Build private diagnostic sheets from original JPEGs and stored Pi geometry."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
import sys
app=Path(__file__).resolve().parents[1];sys.path.insert(0,str(app))
from pklnet_roi import normalize_roi_pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path)
    p.add_argument('--geometry',type=Path,help='Optional complete enrollment geometry export')
    p.add_argument('--include-slowest',action='store_true',help='Also inspect the slowest main query, including a correct result')
    args=p.parse_args()
    repo=app.parents[1];base=args.evidence
    data=json.loads((base/'results.json').read_text());rows={r['sample']:r for r in json.loads((base/'manifest.json').read_text())}
    geometry=json.loads((args.geometry or base/'template-geometry.json').read_text())['records']
    enrolled={}
    for r in geometry:enrolled.setdefault((r['case'],r['identity'].replace(':','-')),[]).append(r)
    out=base/'failure-images';out.mkdir(exist_ok=True);metrics=[]
    def original(sample):
        row=rows[sample]
        with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
        assert hashlib.sha256(value).hexdigest()==row['sha256']
        return Image.open(io.BytesIO(value)).convert('RGB')
    def quad(source):
        points=np.asarray([[0,0,1],[384,0,1],[384,384,1],[0,384,1.]])@np.linalg.inv(source).T
        return points[:,:2]/points[:,2:]
    def overlay(full,source,bounds):
        pixels=np.asarray(full).copy();cv2.polylines(pixels,[np.rint(quad(source)).astype(np.int32)],True,(0,255,0),max(3,full.width//400))
        result=Image.fromarray(pixels);result.thumbnail(bounds);return result
    def crop(full,source):
        gray=cv2.cvtColor(np.asarray(full),cv2.COLOR_RGB2GRAY)
        raw=cv2.warpPerspective(gray,np.diag([1/3,1/3,1])@source,(128,128))
        return normalize_roi_pixels(raw),raw
    slowest=max((q for run in data['runs'] for q in run['queries']),key=lambda q:q['ms'])
    for run in data['runs']:
        for trial in run['queries']:
            if trial['correct'] and not (args.include_slowest and trial is slowest):continue
            sample=trial['sample'];source=np.asarray(trial['diagnostics']['source_matrix'])
            full=original(sample);roi=np.asarray(Image.open(base/trial['roi_artifact']).convert('L'))
            _,raw=crop(full,source)
            metrics.append(dict(case=run['case'],sample=sample,raw_mean=float(raw.mean()),raw_std=float(raw.std()),
                normalized_std=float(roi.std()),normalized_laplacian_var=float(cv2.Laplacian(roi,cv2.CV_64F).var())))
            canvas=Image.new('RGB',(1500,1270),'#17212e');draw=ImageDraw.Draw(canvas)
            canvas.paste(overlay(full,source,(1000,550)),(0,40));canvas.paste(Image.fromarray(roi).resize((300,300),Image.Resampling.NEAREST),(1050,70))
            draw.text((10,10),f'{sample} | {trial["identity"]} | actual Pi query ROI',fill='white')
            draw.text((1050,390),f'predicted: {trial["result"].get("user_id")}\nscore: {trial["result"].get("score")}\nsecond: {trial["result"].get("second_score")}',fill='white')
            for row_number,(label,user) in enumerate((('TRUE',trial['identity'].replace(':','-')),('PREDICTED',trial['result'].get('user_id')))):
                y=620+row_number*320;draw.text((10,y-22),f'{label} enrollment: {user} (stored Pi transforms; grayscale reconstructed locally)',fill='white')
                for index,record in enumerate(enrolled.get((run['case'],user),[])):
                    image=original(record['sample']);matrix=np.asarray(record['source_matrix']);pixels,_=crop(image,matrix)
                    canvas.paste(overlay(image,matrix,(285,165)),(index*300,y));canvas.paste(Image.fromarray(pixels).resize((128,128)),(index*300,y+170))
                    draw.text((index*300+140,y+190),f'enroll #{index+1}',fill='white')
            canvas.save(out/(run['case']+'-'+sample+'.jpg'),quality=90)
    (base/'failure-image-metrics.json').write_text(json.dumps(metrics,indent=2))
    print('built failure sheets',len(metrics))


if __name__=='__main__':main()
