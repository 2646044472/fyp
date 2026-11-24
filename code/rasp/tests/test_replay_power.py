import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from replay_ready_queries import power_fault


@pytest.mark.parametrize('flags', ['throttled=0x1', 'throttled=0x10000',
                                  'throttled=0x50000', '', 'throttled=bad-value'])
def test_power_guard_stops_on_current_historical_or_unreadable_flags(flags):
    assert power_fault({'get_throttled': flags})


def test_power_guard_accepts_only_clean_reading():
    assert not power_fault({'get_throttled': 'throttled=0x0'})
    assert power_fault({})
