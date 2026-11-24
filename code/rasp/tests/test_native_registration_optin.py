from pathlib import Path
from biometric import load_algorithm
import native_registration


def test_native_backend_is_explicit_and_instance_local(monkeypatch):
    root=Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python'
    first=load_algorithm(root,'FastCCDemo-v6')
    second=load_algorithm(root,'FastCCDemo-v6')
    sentinel=object()
    monkeypatch.setattr(native_registration,'NativeRegistration',lambda path,threads: sentinel)
    try:
        original=second.registration
        native_registration.enable_native_registration(first,'explicit-library.so',2)
        assert first.registration is sentinel and first.legacy.registration is sentinel
        assert second.registration is original and second.legacy.registration is not sentinel
    finally:
        first.close();second.close()
