"""Plan an isolated GPU environment and audit paired records; never run a model.

This tool neither installs dependencies nor retries an installation failure.
PyPI access is metadata-only. Private sample bindings stay under runtime/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import urllib.request

APP = Path(__file__).resolve().parents[1]
ROOT_PINS = (
    'onnxruntime-gpu[cuda,cudnn]==1.31.1',
    'numpy==2.3.5', 'scipy==1.16.3', 'Pillow==12.0.0',
    'opencv-contrib-python-headless==5.0.0.93', 'psutil==7.0.0',
    'flatbuffers==25.12.19', 'packaging==25.0', 'protobuf==7.36.2',
    # NVIDIA's CUDA 13.0 Update 2 component table; avoid latest CUDA 13.x drift.
    'nvidia-cuda-runtime==13.0.96', 'nvidia-cuda-nvrtc==13.0.88',
    'nvidia-cublas==13.1.0.3', 'nvidia-cufft==12.0.0.61',
    'nvidia-curand==10.4.0.35', 'nvidia-cudnn-cu13==9.13.1.26',
    'nvidia-nvjitlink==13.0.88',
)
TOLERANCES = {
    'localizer_outputs': {'atol': 1e-4, 'rtol': 1e-5},
    'embedding_outputs': {'atol': 1e-5, 'rtol': 1e-4},
    'identity_scores': {'atol': 1e-7, 'rtol': 1e-6},
}
RESOURCE_LIMITS = {'start_free_GiB': 12, 'running_free_GiB': 2, 'max_RSS_GiB': 14}


def resource_gate(available: int, rss: int, *, startup: bool) -> None:
    """Fail at the frozen boundaries; callers must not retry a failed start."""
    minimum = RESOURCE_LIMITS['start_free_GiB' if startup else 'running_free_GiB'] * 2**30
    if available < minimum or rss >= RESOURCE_LIMITS['max_RSS_GiB'] * 2**30:
        raise MemoryError('Frozen RAM/RSS boundary; no automatic retry')


def placement(profile: list[dict]) -> dict:
    """Use executed node events, rather than an advertised provider list."""
    counts = {}
    for event in profile:
        args = event.get('args', {})
        provider, op = args.get('provider'), args.get('op_name')
        if (event.get('cat') == 'Node' and event.get('name', '').endswith('_kernel_time')
                and event.get('dur', 0) > 0 and provider and op):
            counts[provider, op] = counts.get((provider, op), 0) + 1
    cuda = sum(n for (provider, _), n in counts.items() if provider == 'CUDAExecutionProvider')
    cpu = {op: n for (provider, op), n in counts.items() if provider == 'CPUExecutionProvider'}
    cuda_heavy = sum(n for (provider, op), n in counts.items()
                     if provider == 'CUDAExecutionProvider' and op in {'Conv', 'FusedConv', 'MatMul', 'Gemm'})
    heavy_fallback = {op: n for op, n in cpu.items() if op in {'Conv', 'FusedConv', 'MatMul', 'Gemm'}}
    return dict(cuda_node_events=cuda, cuda_heavy_node_events=cuda_heavy,
                cpu_node_events=cpu, cpu_heavy_fallback=heavy_fallback,
                gpu_execution_proven=cuda > 0 and cuda_heavy > 0 and not heavy_fallback)


def array_comparison(left, right, kind: str) -> dict:
    import numpy as np
    a, b = np.asarray(left), np.asarray(right)
    same_shape = a.shape == b.shape
    finite = bool(np.isfinite(a).all() and np.isfinite(b).all())
    close = same_shape and finite and np.allclose(a, b, **TOLERANCES[kind])
    return dict(same_shape=same_shape, finite=finite, within_tolerance=bool(close),
                max_abs_error=float(np.max(np.abs(a-b))) if same_shape and finite and a.size else None,
                tolerance=TOLERANCES[kind])


def decision_comparison(cpu: dict, gpu: dict) -> dict:
    """Identity/route/ROI differences stop expansion even if scores are close."""
    fields = ('http_status', 'status', 'user_id', 'recognition_route', 'outcome')
    same_labels = all(cpu[k] == gpu[k] for k in fields)
    same_identities = set(cpu['scores']) == set(gpu['scores'])
    keys = sorted(cpu['scores']) if same_identities else []
    scores = array_comparison([cpu['scores'][k] for k in keys],
                              [gpu['scores'][k] for k in keys], 'identity_scores')
    same_roi = cpu['roi_sha256'] == gpu['roi_sha256']
    return dict(decision_exact=same_labels, score_identities_exact=same_identities,
                scores=scores, roi_pixels_exact=same_roi,
                passed=same_labels and same_identities and scores['within_tolerance'] and same_roi)


def read_pypi(name: str, version: str | None = None) -> dict:
    suffix = f'/{version}' if version else ''
    url = f'https://pypi.org/pypi/{name}{suffix}/json'
    with urllib.request.urlopen(url, timeout=25) as response:
        return json.load(response)


def dependency_plan(fetch=read_pypi) -> dict:
    """Validate exact pins against PyPI metadata and this interpreter's tags.

    For unpinned transitives, only the current release is considered. Conflicts
    stop planning; this deliberately is not a backtracking package installer.
    """
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    from packaging.tags import sys_tags
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.specifiers import SpecifierSet
    env = default_environment()
    supported = set(sys_tags())
    constraints, extras, chosen, queue = {}, {}, {}, []

    def add(text):
        req = Requirement(text)
        key = canonicalize_name(req.name)
        constraints.setdefault(key, set()).add(str(req.specifier))
        before = extras.setdefault(key, set()).copy()
        extras[key].update(req.extras)
        if key not in chosen or extras[key] != before:
            queue.append(key)
        if key in chosen and chosen[key]['version'] not in req.specifier:
            raise ValueError(f'Metadata conflict for {key}; do not install')

    for pin in ROOT_PINS:
        add(pin)
    while queue:
        key = queue.pop(0)
        if key not in chosen:
            combined = SpecifierSet(','.join(sorted(constraints[key])))
            exact = [s.version for s in combined if s.operator == '==']
            data = fetch(key, exact[0] if exact else None)
            version = data['info']['version']
            if version not in combined:
                raise ValueError(f'Latest {key} does not satisfy pins; manual review required')
            py_req = data['info'].get('requires_python') or ''
            if platform.python_version() not in SpecifierSet(py_req):
                raise ValueError(f'Unsupported Python for {key}')
            wheels = []
            for wheel in data['urls']:
                if wheel.get('packagetype') != 'bdist_wheel' or wheel.get('yanked'):
                    continue
                _, _, _, tags = parse_wheel_filename(wheel['filename'])
                if supported.intersection(tags):
                    wheels.append(wheel)
            if not wheels:
                raise ValueError(f'No non-yanked compatible wheel for {key}')
            wheel = sorted(wheels, key=lambda w: w['filename'])[0]
            chosen[key] = dict(version=version, filename=wheel['filename'],
                               sha256=wheel['digests']['sha256'], size=wheel['size'],
                               url=wheel['url'], requires_dist=data['info'].get('requires_dist') or [])
        for text in chosen[key]['requires_dist']:
            req = Requirement(text)
            if req.marker is None or any(req.marker.evaluate({**env, 'extra': extra})
                                         for extra in ['', *sorted(extras[key])]):
                add(text)
    for key, entry in chosen.items():
        if entry['version'] not in SpecifierSet(','.join(sorted(constraints[key]))):
            raise ValueError(f'Unresolved transitive conflict: {key}')
    return dict(schema=1, source='Official PyPI metadata and wheel SHA-256',
                python=platform.python_version(), platform=sys.platform,
                root_pins=list(ROOT_PINS), packages=dict(sorted(chosen.items())),
                metadata_consistent=True, installation_tested=False, gpu_inference_tested=False,
                system_site_packages=False)


def write_plan(destination: Path) -> None:
    if destination.exists():
        raise FileExistsError('Plan output must be new; never overwrite an earlier result')
    plan = dependency_plan()
    destination.mkdir(parents=True)
    (destination/'dependency-plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
    lines = ['# Planned lock only: installation and inference remain unverified.',
             '# Official PyPI; CPython 3.13 Windows x64; no system-site-packages.',
             '# Install only into the separate project venv after the blocker is resolved.']
    lines += [f"{name}=={item['version']} --hash=sha256:{item['sha256']}"
              for name, item in plan['packages'].items()]
    (destination/'requirements-gpu-planned.lock').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(dict(metadata_consistent=True, packages=len(plan['packages']),
                          installation_tested=False, output=str(destination))))


def freeze_panel(source: Path, destination: Path) -> None:
    """Reuse the four authorized device bindings, never the failed repair code."""
    if destination.exists():
        raise FileExistsError('Private panel must be a new output')
    protocol = json.loads(source.read_text(encoding='utf-8'))
    items = [item for item in protocol['items'] if item['domain'] == 'device']
    if [item['label'] for item in items] != ['D1', 'D2', 'D3', 'D4']:
        raise ValueError('Expected the existing four fixed device roles')
    if len({item['case'] for item in items}) != 1 or len({item['row']['sample'] for item in items}) != 4:
        raise ValueError('Invalid paired panel bindings')
    plan = dict(schema=1, source_protocol_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                scope='Windows acceleration correctness preflight; frozen scorer; no repair/public/full168/Pi claim',
                items=items, templates_sha256=protocol['templates_sha256']['device'],
                expected_gallery=protocol['expected_gallery']['device'],
                model_root=protocol['model_root'], models_sha256=protocol['models_sha256'],
                resources=RESOURCE_LIMITS, tolerances=TOLERANCES,
                cuda_options=dict(device_id=0, use_tf32=0, cudnn_conv_algo_search='HEURISTIC',
                                  cudnn_conv_use_max_workspace=0, gpu_mem_limit=4*2**30),
                required_timing=['process_startup', 'session_creation', 'first_inference',
                                 'warmup', 'host_to_device', 'bound_inference', 'device_to_host',
                                 'matching', 'full_http_query'],
                timing_note='Transfer microbenchmarks are separate from host-input full queries; never subtract or add them to invent end-to-end latency.',
                kill_conditions=['resource breach or competing worker', 'model/environment hash mismatch',
                                 'CUDA heavy-op execution not demonstrated', 'CPU heavy-op fallback',
                                 'nonfinite/shape/numeric tolerance failure', 'ROI pixel hash or decision difference'],
                cache_namespace='backend + ORT + CUDA options + model and dependency hashes',
                results_written=False, inference_started=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(plan, stream, indent=2)
    print(json.dumps(dict(panel_frozen=True, labels=[x['label'] for x in items], inference_started=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='mode', required=True)
    plan_parser = subs.add_parser('plan'); plan_parser.add_argument('output', type=Path)
    panel_parser = subs.add_parser('freeze-panel')
    panel_parser.add_argument('source', type=Path); panel_parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.mode == 'plan':
        write_plan(args.output)
    else:
        freeze_panel(args.source, args.output)
