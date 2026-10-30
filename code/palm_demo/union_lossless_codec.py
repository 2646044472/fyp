"""Opt-in variable Union envelope; numeric blocks remain byte-for-byte unchanged.

Resource limits are decode/allocation guards, never image resizing, descriptor
selection or scoring parameters. Legacy v26 is read-only compatible. No pickle.
"""
from dataclasses import dataclass
import hashlib
import struct

import cv2
import numpy as np

from registered_matcher import DUAL_SIZE, MAX_POINTS, FastCCDualRegisteredMatcher
from union_matcher import FEATURE_SIZE as LEGACY_SIZE, HEADER as LEGACY_HEADER, MAX_VIEWS

CODEC = 'union-lossless-variable-v2'
TAG = b'UNIONV2\0'
SEMANTIC_MAGIC = 2801066
HEADER = struct.Struct('<8sIIQQIIII')
MAX_NATIVE_SIDE = 16384
MAX_NATIVE_PIXELS = 64*1024*1024
MAX_PNG_BYTES = MAX_NATIVE_PIXELS + 2*1024*1024
MAX_VIEW_BYTES = 88 + MAX_POINTS*520
MAX_FEATURE_BYTES = HEADER.size + DUAL_SIZE + MAX_PNG_BYTES + (MAX_VIEWS+2)*MAX_VIEW_BYTES


def numeric_bytes(value):
    if not isinstance(value, np.ndarray) or value.dtype != np.uint8 or value.ndim != 1 or not value.flags.c_contiguous:
        raise ValueError('Union payload must be contiguous one-dimensional uint8')
    return value


@dataclass
class DecodedUnion:
    parts: tuple
    png: np.ndarray
    gallery_chunks: tuple
    query_chunks: tuple
    storage_codec: str
    used: int

    @property
    def chunks(self):
        return (self.parts[0], self.png, *self.gallery_chunks, *self.query_chunks)

    def logical_sha256(self):
        value=hashlib.sha256(struct.pack('<III',SEMANTIC_MAGIC,len(self.query_chunks),len(self.gallery_chunks)))
        for chunk in self.chunks:
            value.update(struct.pack('<Q',chunk.size));value.update(memoryview(chunk))
        return value.hexdigest()


def decode(feature, *, decode_native=True):
    f=numeric_bytes(feature)
    if f.size>MAX_FEATURE_BYTES or f.size<LEGACY_HEADER+DUAL_SIZE:
        raise ValueError('Union payload allocation limit or minimum length')
    if f.size>=HEADER.size and f[:8].tobytes()==TAG:
        tag,version,semantic,used,encoded,nq,ng,flags,header=HEADER.unpack_from(f)
        if version!=2 or semantic!=SEMANTIC_MAGIC or flags!=0 or header!=HEADER.size or used!=f.size:
            raise ValueError('Invalid variable Union header/version/length')
        codec=CODEC;start=HEADER.size
    else:
        if f.size!=LEGACY_SIZE:
            raise ValueError('Unsupported legacy Union shape')
        semantic,used,encoded,nq,ng=map(int,f[:LEGACY_HEADER].view('<i4'))
        if semantic!=SEMANTIC_MAGIC or not LEGACY_HEADER+DUAL_SIZE<=used<=LEGACY_SIZE:
            raise ValueError('Unsupported legacy Union version/header')
        # Canonical old packers fill padding with zero. Do not silently discard
        # noncanonical hidden bytes during an explicit format migration.
        if np.any(f[used:]):
            raise ValueError('Nonzero legacy padding is not a canonical template')
        codec='union-fixed-v26';start=LEGACY_HEADER
    if (not start+DUAL_SIZE<=used<=f.size or not 0<=encoded<=MAX_PNG_BYTES
            or encoded>used-start-DUAL_SIZE or not 0<=nq<=MAX_VIEWS or ng not in (0,2)
            or (nq and ng!=2) or (nq and not encoded)):
        raise ValueError('Invalid Union counts/lengths')
    legacy=f[start:start+DUAL_SIZE]
    primary,secondary=FastCCDualRegisteredMatcher._views(legacy)
    width,height=primary[3]
    if max(width,height)>MAX_NATIVE_SIDE or width*height>MAX_NATIVE_PIXELS:
        raise ValueError('Native image resource limit')
    pos=start+DUAL_SIZE;png=f[pos:pos+encoded];native=None
    if encoded:
        if (encoded<33 or png[:8].tobytes()!=b'\x89PNG\r\n\x1a\n' or png[12:16].tobytes()!=b'IHDR'
                or int.from_bytes(png[8:12].tobytes(),'big')!=13
                or (int.from_bytes(png[16:20].tobytes(),'big'),int.from_bytes(png[20:24].tobytes(),'big'))!=(width,height)
                or min(width,height)<=0 or png[24]!=8 or png[25]!=0):
            raise ValueError('Invalid native grayscale PNG header/dimensions')
        if decode_native:
            native=cv2.imdecode(png,cv2.IMREAD_GRAYSCALE)
            if native is None or native.dtype!=np.uint8 or native.shape!=(height,width):
                raise ValueError('Invalid native PNG decode')
    pos+=encoded;views=[];chunks=[]
    for index in range(ng+nq):
        begin=pos
        if pos+88>used: raise ValueError('Truncated Union view')
        sigma,n,lower,upper=map(int,f[pos:pos+16].view('<i4'))
        if (sigma not in (0,2,4,8) or not 0<=n<=MAX_POINTS or (lower,upper) not in ((0,384),(-192,576))
                or pos+88+n*520>used):
            raise ValueError('Invalid Union view header/length')
        source=f[pos+16:pos+88].view('<f8').reshape(3,3);pos+=88
        points=f[pos:pos+n*8].view('<f4').reshape(n,2);pos+=n*8
        descriptors=f[pos:pos+n*512].view('<f4').reshape(n,128);pos+=n*512
        if (not np.isfinite(source).all() or abs(np.linalg.det(source))<1e-12
                or not np.isfinite(points).all() or (points<lower).any() or (points>=upper).any()
                or not np.isfinite(descriptors).all() or (descriptors<0).any()):
            raise ValueError('Invalid Union descriptor data')
        views.append((sigma,source,points,descriptors));chunks.append(f[begin:pos])
    if pos!=used or (ng and [v[0] for v in views[:ng]]!=[4,8]):
        raise ValueError('Invalid Union payload layout/trailing data')
    return DecodedUnion((legacy,primary,secondary,native,views[:ng],views[ng:]),png,
                        tuple(chunks[:ng]),tuple(chunks[ng:]),codec,int(used))


def pack(legacy,png,queries,gallery):
    legacy,png=numeric_bytes(legacy),numeric_bytes(png)
    queries,gallery=tuple(queries),tuple(gallery)
    if len(queries)>MAX_VIEWS or len(gallery) not in (0,2) or png.size>MAX_PNG_BYTES:
        raise ValueError('Union view/PNG resource limit; no views dropped')
    chunks=(legacy,png,*(numeric_bytes(c) for c in gallery),*(numeric_bytes(c) for c in queries))
    if legacy.size!=DUAL_SIZE or any(c.size>MAX_VIEW_BYTES for c in chunks[2:]):
        raise ValueError('Invalid Union block size')
    used=HEADER.size+sum(c.size for c in chunks)
    if used>MAX_FEATURE_BYTES: raise ValueError('Union payload resource limit; no views dropped')
    output=np.empty(used,np.uint8)
    output[:HEADER.size]=np.frombuffer(HEADER.pack(TAG,2,SEMANTIC_MAGIC,used,png.size,len(queries),len(gallery),0,HEADER.size),np.uint8)
    pos=HEADER.size
    for chunk in chunks:
        output[pos:pos+chunk.size]=chunk;pos+=chunk.size
    decode(output,decode_native=False)
    return output


def convert_legacy(feature):
    """Explicit lossless conversion; caller must separately authorize reuse."""
    decoded=decode(feature,decode_native=False)
    if decoded.storage_codec!='union-fixed-v26': raise ValueError('Expected canonical legacy v26')
    return pack(decoded.parts[0],decoded.png,decoded.query_chunks,decoded.gallery_chunks)
