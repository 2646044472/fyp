import json
from types import SimpleNamespace
import numpy as np
import pytest
from acceptance_policy import AcceptancePolicy, load_acceptance_policy
from demo_flow import DemoFlow


def document():
    return dict(version=1, name='test-profile', profiles={
        'fastcc': dict(max_distance=.4, min_margin=.02),
        'compnet': dict(max_distance=.25, min_margin=.08),
        'quality': dict(max_distance=.32, min_margin=.08)})


def test_score_families_cannot_borrow_fastcc_limits():
    policy = AcceptancePolicy(document())
    assert policy.rejection(.3, .4, 'pose_confident') is None
    assert policy.rejection(.3, .4, 'compnet_evidence_confident') == ('UNKNOWN', 'POLICY_SCORE_ABOVE_THRESHOLD')
    assert policy.rejection(.3, .4, 'new_unregistered_metric') == ('RETRY', 'UNCONFIGURED_SCORE_FAMILY')


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -.01, 1.01, True, '0.02'])
def test_invalid_configuration_fails_startup(value):
    config = document(); config['profiles']['fastcc']['min_margin'] = value
    with pytest.raises(ValueError): AcceptancePolicy(config)


def test_missing_file_is_opt_in_and_malformed_file_is_not_silently_disabled(tmp_path):
    path = tmp_path/'demo_acceptance_policy.json'
    assert load_acceptance_policy(path) is None
    path.write_text('{}')
    with pytest.raises(ValueError): load_acceptance_policy(path)


def test_ties_single_candidate_and_invalid_scores_never_accept():
    p = AcceptancePolicy(document())
    for best, second in ((.1, .1), (.1, None), (float('nan'), .3), (.1, float('inf')), (.3, .2)):
        assert p.rejection(best, second, 'exhaustive_retained_fastcc_pilot')[0] == 'RETRY'


class PreparedAlgorithm:
    name = 'policy-integration-test'
    def __init__(self): self.scores = {'a': .30, 'b': .40}
    def prepare_probe(self, feature): return SimpleNamespace(route='pose_confident')
    def prepare_enrollment(self, features): return features
    def prepared_bytes(self, value): return value.nbytes
    def score_prepared(self, query, enrolled): raise AssertionError('global scoring required')
    def score_gallery(self, query, groups): return {u: self.scores[u] for u in groups}


def test_rejection_clears_stale_token_and_cannot_confirm_payment(tmp_path):
    (tmp_path/'demo_acceptance_policy.json').write_text(json.dumps(document()))
    algorithm = PreparedAlgorithm()
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(1), '', 'replay'))
    for user in ('a', 'b'):
        flow.store.save(user, np.zeros((5, 1)), {'capture_profile': 'noir-ir'})
        flow.payments.create_account(user, user, 10000)
    good = flow.identify(); assert good['status'] == 'MATCH' and good['token'] in flow.pending
    algorithm.scores = {'a': .30, 'b': .31}
    ambiguous = flow.identify()
    assert ambiguous['status'] == 'RETRY' and 'token' not in ambiguous and 'user_id' not in ambiguous
    assert not flow.pending
    with pytest.raises(ValueError): flow.confirm(good['token'], 'a')
    algorithm.scores = {'a': .45, 'b': .55}
    unknown = flow.identify()
    assert unknown['status'] == 'UNKNOWN' and 'token' not in unknown
    assert flow.payments.transaction_count() == 0 and flow.payments.balance_for('a') == 10000


def test_nonfinite_score_is_rejected_even_without_opt_in_policy(tmp_path):
    algorithm = PreparedAlgorithm()
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(1), '', 'replay'))
    for user in ('a', 'b'):
        flow.store.save(user, np.zeros((5, 1)), {'capture_profile': 'noir-ir'})
        flow.payments.create_account(user, user, 10000)
    algorithm.scores['a'] = float('nan')
    result = flow.identify()
    assert result['status'] == 'RETRY' and result['reason'] == 'INVALID_MATCH_SCORES'
    assert 'token' not in result and not flow.pending
