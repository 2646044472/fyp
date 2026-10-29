"""Check that diagnostic timing never adds parallel worker time to HTTP."""
import importlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest


@pytest.fixture
def tree(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('profile_exclusive_query_tree')
    value=module.TimingTree()
    yield value
    value.close()


def test_nested_request_exclusive_time_reconciles(tree):
    class Work:
        def child(self):return 7
        def root(self):return self.child()+self.child()
    tree.wrap(Work,'root','request');tree.wrap(Work,'child','child')
    tree.begin();assert Work().root()==14;nodes=tree.end()
    root=next(n for n in nodes if n['label']=='request')
    children=[n for n in nodes if n['label']=='child']
    assert len(children)==2 and all(n['parent']==root['id'] for n in children)
    assert sum(n['exclusive_ms']for n in nodes)==pytest.approx(root['inclusive_ms'])
    assert all(n['exclusive_ms']>=0 for n in nodes)


def test_worker_time_is_separate_from_request_tree(tree):
    class Work:
        def worker(self):return 'unchanged'
        def request(self):
            with ThreadPoolExecutor(max_workers=1)as pool:return pool.submit(self.worker).result()
    tree.wrap(Work,'request','request');tree.wrap(Work,'worker','worker')
    tree.begin();assert Work().request()=='unchanged';nodes=tree.end()
    root=next(n for n in nodes if n['label']=='request')
    worker=next(n for n in nodes if n['label']=='worker')
    assert root['thread']!=worker['thread']
    assert worker['parent'] is None
    request_nodes=[n for n in nodes if n['thread']==root['thread']]
    assert sum(n['exclusive_ms']for n in request_nodes)==pytest.approx(root['inclusive_ms'])


def test_exception_does_not_leave_stale_parent(tree):
    class Work:
        def fail(self):raise ValueError('expected')
        def next_request(self):return 1
    tree.wrap(Work,'fail','failed');tree.wrap(Work,'next_request','next')
    tree.begin()
    with pytest.raises(ValueError):Work().fail()
    tree.end();tree.begin();assert Work().next_request()==1;nodes=tree.end()
    assert len(nodes)==1 and nodes[0]['parent'] is None
