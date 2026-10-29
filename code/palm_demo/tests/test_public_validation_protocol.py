import pytest
from tools import evaluate_frozen_public as public


def test_filename_labels_preserve_prefix_and_numeric_indices():
    assert public.member_label('PalmBigDataBase/P_F_61_10.bmp')==('F',61,10)
    assert public.member_label('PalmBigDataBase/P_S_61_2.bmp')==('S',61,2)
    entries=[(public.member_label(n)[2],n) for n in ['P_F_61_10.bmp','P_F_61_2.bmp','P_F_61_1.bmp']]
    assert [i for i,n in sorted(entries)]==[1,2,10]
    assert public.member_label('P_G_61_1.bmp') is None


def test_manifest_fingerprint_ignores_object_order_but_detects_label_change():
    a=[dict(sample='x',identity='a',index=6)]
    assert public.canonical(a)==public.canonical([dict(index=6,identity='a',sample='x')])
    assert public.canonical(a)!=public.canonical([dict(sample='x',identity='b',index=6)])


def test_frozen_source_tolerates_only_newline_encoding(tmp_path,monkeypatch):
    path=tmp_path/'component.py';path.write_bytes(b'value=1\r\n')
    expected=public.source_sha(path);path.write_bytes(b'value=1\n')
    assert public.source_sha(path)==expected
    monkeypatch.setattr(public,'APP',tmp_path)
    protocol=dict(evaluator_sha256=public.source_sha(public.__file__),code_hashes={'component.py':expected})
    public.verify(protocol)
    path.write_bytes(b'value=2\n')
    with pytest.raises(AssertionError,match='Frozen code mismatch'):public.verify(protocol)
