"""Opt-in bounded five-frame numeric archive with a single atomic commit.

CRC/SHA detect corruption, not authenticated tampering. No encryption/pickle.
Native pixels and descriptors remain private biometric template contents.
"""
import hashlib
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import zipfile

import numpy as np

from templates import TemplateStore,safe_user_id
from union_lossless_codec import CODEC,MAX_FEATURE_BYTES,LEGACY_SIZE,decode

SCHEMA='union-five-frame-npz-v2'
FRAME_COUNT=5
MAX_MANIFEST_BYTES=64*1024
MAX_NPY_HEADER_BYTES=1024
MAX_ARCHIVE_EXPANDED_BYTES=FRAME_COUNT*(MAX_FEATURE_BYTES+MAX_NPY_HEADER_BYTES)+MAX_MANIFEST_BYTES


def _preflight_zip(source,count):
    """Bound the central directory before ZipFile constructs member objects."""
    if not hasattr(source,'read'):
        with Path(source).open('rb') as stream:return _preflight_zip(stream,count)
    size=os.fstat(source.fileno()).st_size
    if not 22<=size<=MAX_ARCHIVE_EXPANDED_BYTES+2*1024*1024:raise ValueError('Archive file-size resource limit')
    source.seek(-22,os.SEEK_END);fields=struct.unpack('<4sHHHHIIH',source.read(22));source.seek(0)
    tag,disk,central_disk,disk_count,total,central_bytes,offset,comment=fields
    if (tag!=b'PK\x05\x06' or disk or central_disk or disk_count!=count or total!=count or comment
            or central_bytes>16384 or offset+central_bytes!=size-22):
        raise ValueError('Invalid archive footer/member-count/central-directory limit')


@contextmanager
def _open_archive(path,count):
    # Pin one inode/generation across preflight and decoding; an atomic writer
    # cannot swap an unchecked archive into the interval between two opens.
    with path.open('rb') as source:
        _preflight_zip(source,count)
        with zipfile.ZipFile(source) as archive:yield archive


def digest(array):return hashlib.sha256(memoryview(array)).hexdigest()


def _json_no_duplicates(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('Duplicate manifest key')
        value[key]=item
    return value


def _members(archive,expected):
    infos=archive.infolist()
    if len(infos)!=len(expected) or {i.filename for i in infos}!=set(expected):
        raise ValueError('Unexpected, missing or duplicate archive members')
    if sum(i.file_size for i in infos)>MAX_ARCHIVE_EXPANDED_BYTES:
        raise ValueError('Archive expanded-size resource limit')
    for info in infos:
        if info.flag_bits&1 or info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) or info.is_dir() or info.file_size<0:
            raise ValueError('Unsupported/encrypted archive member')
    return {i.filename:i for i in infos}


def _read_npy(archive,info,shape):
    """Check declared expansion, numeric header and shape before allocating."""
    expected=math.prod(shape)
    if expected>MAX_ARCHIVE_EXPANDED_BYTES or not expected+10<=info.file_size<=expected+MAX_NPY_HEADER_BYTES:
        raise ValueError('NPY member length resource limit')
    with archive.open(info) as stream:
        version=np.lib.format.read_magic(stream)
        header_start=stream.tell()
        if version not in ((1,0),(2,0)):raise ValueError('Unsupported NPY version')
        length_bytes=2 if version==(1,0) else 4
        raw=stream.read(length_bytes)
        if len(raw)!=length_bytes or int.from_bytes(raw,'little')>MAX_NPY_HEADER_BYTES:
            raise ValueError('NPY header resource limit')
        stream.seek(header_start)
        if version==(1,0):actual,fortran,dtype=np.lib.format.read_array_header_1_0(stream,max_header_size=MAX_NPY_HEADER_BYTES)
        elif version==(2,0):actual,fortran,dtype=np.lib.format.read_array_header_2_0(stream,max_header_size=MAX_NPY_HEADER_BYTES)
        else:raise ValueError('Unsupported NPY version')
        if tuple(actual)!=tuple(shape) or fortran or dtype!=np.dtype('uint8'):
            raise ValueError('Invalid numeric frame shape/dtype/order')
        if expected>MAX_ARCHIVE_EXPANDED_BYTES or stream.tell()>MAX_NPY_HEADER_BYTES or info.file_size!=stream.tell()+expected:
            raise ValueError('NPY header/member length mismatch')
        result=np.empty(shape,np.uint8);view=memoryview(result).cast('B');position=0
        while position<expected:
            count=stream.readinto(view[position:min(expected,position+1024*1024)])
            if not count:raise ValueError('Truncated numeric frame')
            position+=count
        if stream.read(1):raise ValueError('Trailing numeric frame data')
        return result


class LosslessTemplateStore:
    cache_namespace=(SCHEMA,CODEC)

    def __init__(self,root,*,compression_level=None):
        if compression_level is None:compression_level=1
        if type(compression_level)!=int or not 1<=compression_level<=9:raise ValueError('Invalid compression level')
        self.root=Path(root);self.compression_level=compression_level

    def _new_path(self,user):return self.root/(safe_user_id(user)+'.union2.npz')
    def _legacy_paths(self,user):return TemplateStore(self.root).paths(user)

    def paths(self,user):
        new=self._new_path(user);old=self._legacy_paths(user)
        if new.exists():
            if any(p.exists() for p in old):raise ValueError('Ambiguous legacy/new template; use an isolated root')
            return (new,)
        return old

    def exists(self,user):return all(p.is_file() for p in self.paths(user))

    @staticmethod
    def batch_features(features):
        frames=tuple(features)
        if len(frames)!=FRAME_COUNT:raise ValueError('Exactly five frames required')
        for frame in frames:decode(frame,decode_native=False)
        return frames

    def save(self,user,features,metadata):
        user=safe_user_id(user)
        if any(p.exists() for p in self._legacy_paths(user)):
            raise ValueError('Legacy migration requires a new isolated root')
        frames=self.batch_features(features)
        if any(decode(f,decode_native=False).storage_codec!=CODEC for f in frames):
            raise ValueError('New archive requires explicit new-codec frames')
        metadata=dict(metadata)
        if metadata.get('user',user)!=user:raise ValueError('Template user mismatch')
        if metadata.get('samples',FRAME_COUNT)!=FRAME_COUNT:raise ValueError('Template frame count mismatch')
        if metadata.get('template_codec',CODEC)!=CODEC or metadata.get('template_storage_schema',SCHEMA)!=SCHEMA:
            raise ValueError('Template metadata codec mismatch')
        metadata.update(user=user,template_codec=CODEC,template_storage_schema=SCHEMA)
        entries=[dict(member=f'frame_{i:03d}.npy',bytes=int(f.size),sha256=digest(f)) for i,f in enumerate(frames)]
        manifest=dict(schema=SCHEMA,codec=CODEC,metadata=metadata,frames=entries)
        raw=json.dumps(manifest,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
        if len(raw)>MAX_MANIFEST_BYTES:raise ValueError('Template manifest resource limit')
        self.root.mkdir(parents=True,exist_ok=True)
        descriptor,temp=tempfile.mkstemp(dir=self.root,prefix='.'+user+'-',suffix='.tmp');temp=Path(temp)
        try:
            with os.fdopen(descriptor,'w+b') as stream:
                with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=self.compression_level) as archive:
                    archive.writestr('manifest.json',raw)
                    for entry,frame in zip(entries,frames):
                        with archive.open(entry['member'],'w',force_zip64=True) as target:
                            np.lib.format.write_array(target,frame,allow_pickle=False)
                stream.flush();os.fsync(stream.fileno())
            os.replace(temp,self._new_path(user))
            if os.name!='nt':
                handle=os.open(self.root,os.O_RDONLY)
                try:os.fsync(handle)
                finally:os.close(handle)
        finally:temp.unlink(missing_ok=True)

    def load(self,user):
        user=safe_user_id(user);paths=self.paths(user)
        if len(paths)==2:return self._load_legacy(user,paths)
        path=paths[0]
        if not path.is_file():raise FileNotFoundError(user)
        names=['manifest.json']+[f'frame_{i:03d}.npy' for i in range(FRAME_COUNT)]
        with _open_archive(path,len(names)) as archive:
            infos=_members(archive,names)
            if infos['manifest.json'].file_size>MAX_MANIFEST_BYTES:raise ValueError('Manifest resource limit')
            manifest=json.loads(archive.read('manifest.json'),object_pairs_hook=_json_no_duplicates)
            if (not isinstance(manifest,dict) or set(manifest)!=set(('schema','codec','metadata','frames'))
                    or manifest['schema']!=SCHEMA or manifest['codec']!=CODEC or not isinstance(manifest['metadata'],dict)
                    or not isinstance(manifest['frames'],list) or len(manifest['frames'])!=FRAME_COUNT):
                raise ValueError('Incompatible template manifest')
            metadata=manifest['metadata']
            if (metadata.get('user')!=user or metadata.get('template_codec')!=CODEC
                    or metadata.get('template_storage_schema')!=SCHEMA):raise ValueError('Invalid template metadata version/user')
            frames=[]
            for index,entry in enumerate(manifest['frames']):
                if (not isinstance(entry,dict) or set(entry)!=set(('member','bytes','sha256'))
                        or entry['member']!=names[index+1] or type(entry['bytes'])!=int
                        or not 0<entry['bytes']<=MAX_FEATURE_BYTES or not isinstance(entry['sha256'],str)
                        or len(entry['sha256'])!=64):raise ValueError('Invalid ordered frame manifest')
                frame=_read_npy(archive,infos[entry['member']],(entry['bytes'],))
                if digest(frame)!=entry['sha256']:raise ValueError('Template frame checksum mismatch')
                if decode(frame,decode_native=False).storage_codec!=CODEC:raise ValueError('Wrong frame codec')
                frame.flags.writeable=False;frames.append(frame)
        return tuple(frames),metadata

    def _load_legacy(self,user,paths):
        data,meta=paths
        if not data.is_file() or not meta.is_file():raise FileNotFoundError(user)
        if meta.stat().st_size>MAX_MANIFEST_BYTES:raise ValueError('Legacy metadata resource limit')
        metadata=json.loads(meta.read_text(encoding='utf-8'),object_pairs_hook=_json_no_duplicates)
        if not isinstance(metadata,dict) or metadata.get('user',user)!=user:raise ValueError('Invalid legacy metadata/user')
        with _open_archive(data,1) as archive:
            info=_members(archive,['features.npy'])['features.npy']
            array=_read_npy(archive,info,(FRAME_COUNT,LEGACY_SIZE))
        frames=tuple(array)
        for frame in frames:
            if decode(frame,decode_native=False).storage_codec!='union-fixed-v26':raise ValueError('Wrong legacy frame version')
        array.flags.writeable=False
        for frame in frames:frame.flags.writeable=False
        return frames,metadata

    def list_users(self):
        if not self.root.exists():return []
        users=set(TemplateStore(self.root).list_users())
        users.update(p.name[:-len('.union2.npz')] for p in self.root.glob('*.union2.npz'))
        for user in users:self.paths(user)
        return sorted(users)

    def delete(self,user):
        for path in self.paths(user):path.unlink(missing_ok=True)
