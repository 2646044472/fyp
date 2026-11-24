import csv

from PIL import Image

from tools import benchmark_pklnet_captures as runner


def capture_rows(tmp_path):
    rows = []
    for label_index, (subject, hand) in enumerate((('p1', 'left'), ('p1', 'right'), ('p2', 'left'), ('p2', 'right'))):
        for index in (1, 6):
            path = tmp_path / f'{subject}-{hand}-{index}.png'
            Image.new('L', (4, 4), 20 + label_index * 30).save(path)
            rows.append({'sample': path.stem, 'subject': subject, 'hand': hand,
                         'sample_index': index, 'roi': str(path), 'saved_old_roi': None, 'status': 'ok'})
    return rows


class ToyMatcher:
    def __init__(self):
        self.extractions = 0

    def extract(self, image):
        self.extractions += 1
        return int(image[0, 0])

    def match(self, first, second):
        return abs(first - second) / 255


def test_multiple_participant_relations_and_identical_branch_reuse(tmp_path, monkeypatch):
    rows = capture_rows(tmp_path)
    algorithm = ToyMatcher()
    monkeypatch.setattr(runner, 'get_algorithm', lambda name: algorithm)
    summaries = runner.benchmark(rows, tmp_path, ['toy'])
    assert algorithm.extractions == 8
    first, passed = summaries
    assert first['same_hand_pairs'] == 4
    assert first['nonmate_pairs'] == 24
    assert first['same_person_other_hand_pairs'] == 8
    assert first['different_person_pairs'] == 16
    assert first['rank1_correct'] == first['rank1_probes'] == 4
    assert passed['timing_reused_from'] == 'pklnet_all'
    pairs = list(csv.DictReader((tmp_path / 'pair_scores.csv').open(newline='')))
    all_pairs = [r for r in pairs if r['branch'] == 'pklnet_all']
    passed_pairs = [r for r in pairs if r['branch'] == 'pklnet_geometry_pass']
    assert len(all_pairs) == len(passed_pairs) == 28
    assert [(r['first'], r['second'], r['distance']) for r in all_pairs] == [(r['first'], r['second'], r['distance']) for r in passed_pairs]


def test_geometry_failure_keeps_full_scores_and_measures_distinct_subset(tmp_path, monkeypatch):
    rows = capture_rows(tmp_path)
    rows[1]['status'] = 'invalid_geometry'
    algorithm = ToyMatcher()
    monkeypatch.setattr(runner, 'get_algorithm', lambda name: algorithm)
    summaries = runner.benchmark(rows, tmp_path, ['toy'])
    assert algorithm.extractions == 8 + 7
    assert [r['images'] for r in summaries] == [8, 7]
    assert 'timing_reused_from' not in summaries[1]
