"""Read public ZIP metadata by verified HTTP Range; no dataset subsampling claim."""
import argparse,collections,hashlib,io,json,re,zipfile
from pathlib import Path
import requests


class HTTPRangeFile(io.RawIOBase):
    def __init__(self,source):
        self.session=requests.Session();self.position=0
        with self.session.get(source,stream=True,timeout=(30,90))as response:
            response.raise_for_status();self.url=response.url;self.size=int(response.headers['Content-Length'])
        self.read_bytes=0
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
        if not 0<=position<=self.size:raise ValueError('Seek outside public archive')
        self.position=position;return position
    def read(self,count=-1):
        count=self.size-self.position if count<0 else min(count,self.size-self.position)
        if count==0:return b''
        if count>32*1024**2:raise ValueError('This inspector only reads metadata/single members')
        lo=self.position;hi=lo+count-1
        response=self.session.get(self.url,headers={'Range':f'bytes={lo}-{hi}'},timeout=(30,90));response.raise_for_status()
        assert response.status_code==206 and response.headers.get('Content-Range')==f'bytes {lo}-{hi}/{self.size}'
        data=response.content;assert len(data)==count;self.position+=len(data);self.read_bytes+=len(data);return data


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('output',type=Path);p.add_argument('--preview',type=Path);a=p.parse_args()
    remote=HTTPRangeFile(a.source)
    with zipfile.ZipFile(remote)as archive:
        files=[dict(name=v.filename,bytes=v.file_size,compressed_bytes=v.compress_size,crc=v.CRC,offset=v.header_offset)for v in archive.infolist()if not v.is_dir()]
        labels=collections.Counter();conditions=collections.Counter();unparsed=[]
        for entry in files:
            match=re.fullmatch(r'(\d{3})_(F|RF|P|RP)_(\d+)\.[jJ][pP][gG]',Path(entry['name']).name)
            if match:labels[match[1]]+=1;conditions[match[2]]+=1
            else:unparsed.append(entry['name'])
        report=dict(complete=True,scope='Every actual ZIP central-directory member; CRC/data integrity not yet checked',source=a.source,
            archive_bytes=remote.size,files=len(files),subjects=len(labels),subject_sample_histogram=dict(collections.Counter(labels.values())),
            conditions=dict(conditions),unparsed=unparsed,uncompressed_bytes=sum(v['bytes']for v in files),inventory=files)
        if a.preview:
            entry=next(v for v in files if re.search(r'_RP_\d+\.',v['name']))
            data=archive.read(entry['name']);a.preview.parent.mkdir(parents=True,exist_ok=True);a.preview.write_bytes(data)
            report['preview']=dict(name=entry['name'],sha256=hashlib.sha256(data).hexdigest())
    report['metadata_read_bytes']=remote.read_bytes
    assert not a.output.exists();a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='inventory'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
