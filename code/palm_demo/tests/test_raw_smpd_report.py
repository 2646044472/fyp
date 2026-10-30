import importlib
from pathlib import Path


def reporting(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('report_raw_smpd')


def query(sample, identity='smpd:001:right', user='smpd-001-right', score=.2, second=.4,
          status='MATCH', http=200, ms=1000):
    return dict(sample=sample,identity=identity,http_status=http,ms=ms,
        result=dict(status=status,user_id=user,score=score,second_score=second))


def test_correct_reject_wrong_tie_and_failure_have_distinct_denominators(monkeypatch):
    report=reporting(monkeypatch)
    rows=[query('correct'),query('slow-correct',ms=2600),query('wrong',user='someone-else'),
          query('tie',second=.2),query('reject',status='NO_MATCH'),query('failure',http=400)]
    s=report.summarize(rows)
    assert s['total']==6 and s['correct']==2 and s['correct_within_2500']==1
    assert s['accuracy']==2/6
    assert s['wrong_identity_accepted']==s['true_identity_nonunique']==s['rejected']==s['processing_failure']==1
    assert s['correct_timing']['n']==2 and s['all_timing']['n']==6


def test_duplicate_diagnostic_uses_filename_before_outcome_and_keeps_conflicts(monkeypatch):
    report=reporting(monkeypatch)
    rows=[dict(sample='enroll',identity='one',sha256='A',enrollment=True),
          dict(sample='b',identity='one',sha256='A',enrollment=False),
          dict(sample='a',identity='two',sha256='A',enrollment=False),
          dict(sample='c',identity='two',sha256='B',enrollment=False)]
    d=report.duplicate_audit(rows,[query('b'),query('c'),query('a',user='wrong')])
    assert d['unique_byte_contents']==2 and d['redundant_files']==2
    assert d['query_files_overlapping_enrollment']==2
    assert d['conflicting_identity_groups'][0]['samples']==['enroll','b','a']
    assert d['unique_content_diagnostic']['total']==2
    assert d['unique_content_diagnostic']['correct']==1
    assert d['unique_content_without_enrollment_overlap']['total']==1
    assert d['unique_content_without_enrollment_overlap']['correct']==1
    assert d['repeated_content_decision_conflicts'][0]['samples']==['a','b']


def test_preexisting_policy_shadow_exposes_coverage_loss_and_remaining_error(monkeypatch):
    report=reporting(monkeypatch)
    rows=[query('correct'),query('lost-correct',score=.36,second=.37),
          query('blocked-wrong',user='wrong',score=.36,second=.37),
          query('remaining-wrong',user='wrong',score=.36,second=.40),query('failure',http=400)]
    for row in rows:row['result']['recognition_route']='exhaustive_retained_fastcc_pilot'
    shadow=report.frozen_policy_shadow(rows)
    assert shadow['correct']==1 and shadow['wrong_identity_accepted']==1
    assert shadow['rejected']==2 and shadow['processing_failure']==1
    assert shadow['lost_previously_correct']==['lost-correct']
    assert shadow['wrong_identities_blocked']==['blocked-wrong']
    assert shadow['genuine_wrong_to_correct']==0
    assert all(r['result']['status']=='MATCH' for r in rows)
