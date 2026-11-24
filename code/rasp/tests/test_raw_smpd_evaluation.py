import hashlib,importlib,io,zipfile
from pathlib import Path
import numpy as np,pytest
from PIL import Image,ImageOps


@pytest.fixture
def evaluator(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('evaluate_raw_smpd')


def test_cross_part_zip_reads_match_standard_zip_decoder(evaluator,tmp_path):
    stream=io.BytesIO();payloads={'root/001_F_0.JPG':bytes(range(256))*20,'root/001_RP_39.JPG':b'other input'*700}
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED)as archive:
        for name,data in payloads.items():archive.writestr(name,data)
    data=stream.getvalue();parts=tmp_path/'parts';parts.mkdir();block=73
    for index,start in enumerate(range(0,len(data),block)):(parts/f'{index:04d}.part').write_bytes(data[start:start+block])
    reader=evaluator.DownloadParts(parts,len(data),block)
    with zipfile.ZipFile(io.BytesIO(data))as archive:
        for name,expected in payloads.items():
            info=archive.getinfo(name);entry=dict(offset=info.header_offset,compressed_bytes=info.compress_size,bytes=info.file_size,crc=info.CRC)
            assert reader.member(entry)==expected
            with pytest.raises(ValueError,match='CRC'):reader.member(dict(entry,crc=entry['crc']^1))


def test_replay_honors_exif_metadata_and_source_hash(evaluator,tmp_path):
    image=Image.fromarray(np.random.default_rng(3).integers(0,256,(24,40,3),dtype=np.uint8));exif=Image.Exif();exif[274]=6
    path=tmp_path/'original.jpg';image.save(path,exif=exif);digest=hashlib.sha256(path.read_bytes()).hexdigest()
    camera=evaluator.ExifReplay();camera.select([dict(original=str(path),sha256=digest)])
    preview,full,_=camera.capture_highres()
    with Image.open(path)as raw:expected=ImageOps.exif_transpose(raw).convert('RGB')
    assert full.size==(24,40);np.testing.assert_array_equal(full,expected)
    camera.select([dict(original=str(path),sha256='wrong')])
    with pytest.raises(RuntimeError,match='INPUT_INTEGRITY'):camera.capture_highres()


def test_windows_memory_allowance_keeps_index_and_retrieval_identical(evaluator):
    from indexed_demo_matcher import IndexedDemoMatcher
    from biometric import load_algorithm
    root=Path(__file__).resolve().parents[1]
    original=IndexedDemoMatcher.prepare_gallery;limit=IndexedDemoMatcher.prepared_cache_limit_bytes
    base=load_algorithm(root/'vendor/palmprint-recognition-python','FastCC');first=IndexedDemoMatcher(base);second=IndexedDemoMatcher(base)
    rng=np.random.default_rng(381);groups={}
    for user in('a','b'):
        samples=[]
        for index in range(5):
            descriptors=rng.random((12,128),dtype=np.float32);descriptors/=np.linalg.norm(descriptors,axis=1,keepdims=True)
            samples.append((None,[(0,np.eye(3),np.zeros((12,2),np.float32),descriptors,np.zeros((32,32),bool))]))
        groups[user]=samples
    query=rng.random((10,128),dtype=np.float32)
    try:
        first.prepare_gallery(groups);expected=first._index.knnMatch(query,k=4)
        evaluator.install_windows_capacity();second.prepare_gallery(groups);actual=second._index.knnMatch(query,k=4)
        assert first._mapping==second._mapping and first._positions==second._positions
        np.testing.assert_array_equal(first._labels,second._labels)
        assert [[(m.trainIdx,m.distance)for m in matches]for matches in actual]==[[(m.trainIdx,m.distance)for m in matches]for matches in expected]
    finally:
        IndexedDemoMatcher.prepare_gallery=original;IndexedDemoMatcher.prepared_cache_limit_bytes=limit;first.close();second.close()
