import copy
import importlib.util
from pathlib import Path
import unittest

import numpy as np

_FILE = Path(__file__).resolve().parents[1]/'tools/gpu_ort_preflight.py'
_SPEC = importlib.util.spec_from_file_location('gpu_ort_preflight', _FILE)
gpu = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(gpu)


class TestGPUValidationBarriers(unittest.TestCase):
    def test_frozen_memory_boundaries(self):
        gib = 2**30
        gpu.resource_gate(12*gib, 13*gib, startup=True)
        gpu.resource_gate(2*gib, gib, startup=False)
        for available, rss, startup in [(12*gib-1, gib, True), (2*gib-1, gib, False),
                                        (20*gib, 14*gib, False)]:
            with self.subTest(available=available, rss=rss, startup=startup):
                with self.assertRaises(MemoryError):
                    gpu.resource_gate(available, rss, startup=startup)

    def test_provider_name_or_copy_event_cannot_prove_gpu_compute(self):
        copies = [{'cat':'Node', 'name':'copy_kernel_time', 'dur':1,
                   'args':{'provider':'CUDAExecutionProvider', 'op_name':'MemcpyFromHost'}}]
        self.assertFalse(gpu.placement([])['gpu_execution_proven'])
        self.assertFalse(gpu.placement(copies)['gpu_execution_proven'])
        conv = {'cat':'Node', 'name':'conv_kernel_time', 'dur':1,
                'args':{'provider':'CUDAExecutionProvider', 'op_name':'Conv'}}
        advertised = dict(conv, name='provider_registration')
        self.assertFalse(gpu.placement(copies+[advertised])['gpu_execution_proven'])
        self.assertTrue(gpu.placement(copies+[conv])['gpu_execution_proven'])
        fallback = {'cat':'Node', 'name':'matmul_kernel_time', 'dur':1,
                    'args':{'provider':'CPUExecutionProvider', 'op_name':'MatMul'}}
        result = gpu.placement(copies+[conv, fallback])
        self.assertFalse(result['gpu_execution_proven'])
        self.assertEqual(result['cpu_heavy_fallback'], {'MatMul':1})

    def test_nonfinite_shape_and_numeric_drift_stop_pair(self):
        a = np.ones((2, 3), dtype=np.float32)
        self.assertTrue(gpu.array_comparison(a, a.copy(), 'embedding_outputs')['within_tolerance'])
        for b in [np.ones((3,2)), np.full((2,3), np.nan), a+.01]:
            self.assertFalse(gpu.array_comparison(a, b, 'embedding_outputs')['within_tolerance'])

    def test_score_tolerance_cannot_hide_decision_or_roi_change(self):
        a = dict(http_status=200, status='MATCH', user_id='synthetic-a', recognition_route='frozen',
                 outcome='wrong_identity_accepted', scores={'synthetic-a':.3,'synthetic-b':.4}, roi_sha256='fixture')
        self.assertTrue(gpu.decision_comparison(a, copy.deepcopy(a))['passed'])
        for field, value in [('user_id','synthetic-b'), ('roi_sha256','changed'),
                             ('recognition_route','different'), ('outcome','correct')]:
            b = copy.deepcopy(a); b[field] = value
            self.assertFalse(gpu.decision_comparison(a, b)['passed'])
        b = copy.deepcopy(a); b['scores'].pop('synthetic-b')
        self.assertFalse(gpu.decision_comparison(a, b)['passed'])
        b = copy.deepcopy(a); b['scores']['synthetic-a'] += .001
        self.assertFalse(gpu.decision_comparison(a, b)['passed'])

    def test_dependency_conflict_stops_without_installing(self):
        def incompatible(name, version):
            return {'info':{'version':'0.0.0'}, 'urls':[]}
        with self.assertRaisesRegex(ValueError, 'does not satisfy pins'):
            gpu.dependency_plan(incompatible)


if __name__ == '__main__':
    unittest.main()
