"""Inventory every file in an author-published public dataset before selection."""
import argparse,collections,json,re,time
from pathlib import Path
import requests


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ref');p.add_argument('output',type=Path);a=p.parse_args()
    assert re.fullmatch(r'[\w-]+/[\w-]+',a.ref)
    metadata=requests.get('https://www.kaggle.com/api/v1/datasets/view/'+a.ref,timeout=40);metadata.raise_for_status();meta=metadata.json()
    files=[];token=None;pages=0;seen=set()
    while True:
        params=dict(pageSize=1000)
        if token:params['pageToken']=token
        response=requests.get('https://www.kaggle.com/api/v1/datasets/list/'+a.ref,params=params,timeout=40);response.raise_for_status();data=response.json()
        batch=data.get('datasetFiles',[]);assert batch and not any(f['name']in seen for f in batch),'Repeated/empty inventory page'
        files.extend(dict(name=f['name'],bytes=f['totalBytes'])for f in batch);seen.update(f['name']for f in batch);pages+=1
        token=data.get('nextPageToken');print(a.ref,pages,len(files),flush=True)
        if not token:break
        assert pages<1000
    photos=[f for f in files if Path(f['name']).suffix.lower()in('.jpg','.jpeg','.bmp','.png','.tif','.tiff')]
    subjects=collections.Counter()
    for f in photos:
        match=re.search(r'(?:/user_(\d+)/|/(\d{3})/)',f['name'])
        if match:subjects[next(v for v in match.groups()if v is not None)]+=1
    report=dict(complete=True,ref=a.ref,title=meta.get('title'),source='https://www.kaggle.com/datasets/'+a.ref,
        description=meta.get('description'),license=meta.get('licenseName'),files=len(files),photo_files=len(photos),
        bytes=sum(f['bytes']for f in files),subjects=len(subjects),subject_sample_histogram=dict(collections.Counter(subjects.values())),
        inventory=files,metadata_reported_bytes=meta.get('totalBytes'),pages=pages)
    assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('description','inventory')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
