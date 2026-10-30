"""Resumable ordinary HTTP Range download, exact size/SHA and full ZIP CRC check.

Only public dataset download endpoints are inputs. Signed redirect URLs stay in
memory; no account credentials, raw private data or signed URLs are logged.
"""
import argparse,hashlib,json,threading,time,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests


def safe_error(error):
    message=type(error).__name__
    for marker in('UNEXPECTED_EOF_WHILE_READING','CERTIFICATE_VERIFY_FAILED','Connection refused','timed out'):
        if marker in str(error):message+=': '+marker
    response=getattr(error,'response',None)
    if response is not None:message+=' HTTP '+str(response.status_code)
    return message


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    assert a.source.startswith('https://www.kaggle.com/api/v1/datasets/download/')and 1<=a.workers<=4
    assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True);parts=a.output.with_suffix('.parts');parts.mkdir(exist_ok=True)
    progress=a.output.with_suffix('.download.json');lock=threading.Lock();start=time.perf_counter()
    report=dict(source=a.source,complete=False,bytes=0,parts={},workers=a.workers);last=[0.]
    def save(force=False):
        if not force and time.perf_counter()-last[0]<10:return
        report['elapsed_s']=time.perf_counter()-start;temp=progress.with_suffix('.tmp');temp.write_text(json.dumps(report,indent=2));temp.replace(progress);last[0]=time.perf_counter()
        print(report['bytes'],report.get('expected_bytes'),round(report['elapsed_s']),flush=True)
    try:
        with requests.get(a.source,stream=True,timeout=(30,90))as first:
            first.raise_for_status();url=first.url;size=int(first.headers.get('Content-Length',0));kind=first.headers.get('Content-Type','')
            assert 'zip'in kind and 0<size<16*1024**3,(first.status_code,kind,size)
        report['expected_bytes']=size;save(True)
        with requests.get(url,headers={'Range':'bytes=0-0'},stream=True,timeout=(30,90))as test:
            test.raise_for_status();assert test.status_code==206 and test.headers.get('Content-Range')==f'bytes 0-0/{size}','Server does not support verified Range downloads'
        block=64*1024**2
        def piece(index,lo,hi):
            path=parts/f'{index:04d}.part';length=hi-lo+1
            if path.exists()and path.stat().st_size==length:
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                with lock:report['bytes']+=length;report['parts'][str(index)]=dict(bytes=length,sha256=digest,resumed=True);save()
                return path
            for attempt in range(3):
                digest=hashlib.sha256();count=0
                try:
                    with requests.get(url,headers={'Range':f'bytes={lo}-{hi}'},stream=True,timeout=(30,90))as response:
                        response.raise_for_status();assert response.status_code==206 and response.headers.get('Content-Range')==f'bytes {lo}-{hi}/{size}'
                        with path.open('wb')as output:
                            for chunk in response.iter_content(1024**2):
                                if not chunk:continue
                                output.write(chunk);digest.update(chunk);count+=len(chunk)
                                with lock:report['bytes']+=len(chunk);save()
                    assert count==length
                    with lock:report['parts'][str(index)]=dict(bytes=count,sha256=digest.hexdigest(),resumed=False,attempts=attempt+1);save(True)
                    return path
                except requests.RequestException as error:
                    with lock:
                        report['bytes']-=count;report.setdefault('transport_retries',[]).append(dict(part=index,attempt=attempt+1,error=safe_error(error)));save(True)
                    if attempt==2 or getattr(getattr(error,'response',None),'status_code',None)in(401,403):raise
                    time.sleep(attempt+1)
        ranges=[(i,lo,min(size-1,lo+block-1))for i,lo in enumerate(range(0,size,block))]
        with ThreadPoolExecutor(max_workers=a.workers)as pool:
            futures=[pool.submit(piece,*item)for item in ranges]
            for future in as_completed(futures):future.result()
        combined=a.output.with_suffix('.assembling');digest=hashlib.sha256();total=0
        with combined.open('wb')as output:
            for i,lo,hi in ranges:
                with(parts/f'{i:04d}.part').open('rb')as source:
                    while chunk:=source.read(4*1024**2):output.write(chunk);digest.update(chunk);total+=len(chunk)
        assert total==size and report['bytes']==size
        with zipfile.ZipFile(combined)as archive:
            bad=archive.testzip();assert bad is None,('ZIP CRC failure',bad)
            report['zip_members']=len(archive.infolist())
        combined.replace(a.output);report.update(complete=True,sha256=digest.hexdigest(),zip_crc_checked=True);save(True)
    except Exception as error:
        with lock:report['error']=safe_error(error);save(True)
        raise RuntimeError(safe_error(error))from None


if __name__=='__main__':main()
