import importlib
from pathlib import Path

import pytest


@pytest.fixture
def limits(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('experiment_resource_limits')


@pytest.mark.parametrize('startup,minimum', [(True, 12), (False, 2)])
def test_available_memory_byte_boundaries(limits, startup, minimum):
    boundary = minimum*limits.GIB
    assert limits.resource_fault(boundary, limits.MAX_RSS_BYTES, startup=startup) is None
    assert limits.resource_fault(boundary+1, limits.MAX_RSS_BYTES, startup=startup) is None
    assert limits.resource_fault(boundary-1, 0, startup=startup) == (
        'startup_available_ram' if startup else 'running_available_ram')


@pytest.mark.parametrize('startup', [False, True])
def test_exactly_14_gib_is_allowed_but_one_byte_more_is_rejected(limits, startup):
    available = 12*limits.GIB
    assert limits.resource_fault(available, 14*limits.GIB-1, startup=startup) is None
    assert limits.resource_fault(available, 14*limits.GIB, startup=startup) is None
    assert limits.resource_fault(available, 14*limits.GIB+1, startup=startup) == 'rss_above_limit'


@pytest.mark.parametrize('name', ['pilot_gallery_lifecycle', 'audit_global_sift_geometry'])
def test_both_drivers_share_the_authorized_boundary_without_launching(limits, name):
    driver = importlib.import_module(name)
    assert driver.resource_fault is limits.resource_fault
    assert driver.resource_fault(12*limits.GIB, 14*limits.GIB, startup=True) is None
