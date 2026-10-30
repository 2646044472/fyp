"""Read-only migration audit; never starts inference or rewrites a frozen run.

Use --map OLD_ROOT=NEW_ROOT for absolute paths embedded by the original host.
The mapping is for verification only: it does not authorize cross-host resume.
"""
import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_RESULTS = '19dbd849fc65b09c2a42045975e5a2ccf267e07352a9450b0a467153efdc48fa'
EXPECTED_LEDGER = 'a9d967c51197f471f2cdde02d428d26131358304741bf552af389291abbf9eaf'


def digest(path, normalized=False):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        if normalized:
            value.update(stream.read().replace(b'\r\n', b'\n'))
        else:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                value.update(block)
    return value.hexdigest()


def relocate(value, mappings):
    # Windows drive paths must be handled lexically on Linux.
    name = str(value).replace('\\', '/').rstrip('/')
    for old, new in sorted(mappings, key=lambda pair: len(pair[0]), reverse=True):
        prefix = old.replace('\\', '/').rstrip('/')
        if name == prefix or name.startswith(prefix + '/'):
            return Path(new) / name[len(prefix):].lstrip('/')
    return Path(name)


def validate_prefix(rows, report, raw):
    if raw and not raw.endswith(b'\n'):
        raise ValueError('Incomplete ledger record; preserve bytes without truncating')
    queries = [json.loads(line) for line in raw.splitlines() if line]
    if queries != report['queries']:
        raise ValueError('Report and ledger disagree')
    ordered = sorted((r for r in rows if not r['enrollment']), key=lambda r: (r['subject'], r['index']))
    names = [q['sample'] for q in queries]
    if len(names) != len(set(names)) or names != [r['sample'] for r in ordered[:len(names)]]:
        raise ValueError('Completed records are not the unique frozen prefix')
    by_sample = {r['sample']: r for r in ordered}
    if any(q['identity'] != by_sample[q['sample']]['identity'] for q in queries):
        raise ValueError('Query truth differs from frozen manifest')
    return queries, len(ordered)


def audit(root, app, compnet, pklnet, mappings=()):
    checks = []
    def check(name, path, expected=None, normalized=False):
        item = dict(name=name, path=str(path), exists=path.is_file())
        if item['exists']:
            item.update(bytes=path.stat().st_size, sha256=digest(path, normalized))
        item['ok'] = item['exists'] and (expected is None or item['sha256'] == expected)
        checks.append(item)
        return item['ok']
    files = {name: root / name for name in ('protocol.json', 'dependency-lock.json',
        'zip-inventory.json', 'SMPD.download.json', 'prepared/progress.json',
        'prepared/manifest.json', 'evaluation/results.json', 'evaluation/queries.jsonl')}
    present = [check(name, path) for name, path in files.items()]
    if not all(present):
        return dict(ready_for_parity_check=False, checks=checks, errors=['Checkpoint incomplete'])
    load = lambda name: json.loads(files[name].read_text(encoding='utf-8'))
    protocol, rows, report = load('protocol.json'), load('prepared/manifest.json'), load('evaluation/results.json')
    check('known_241_results', files['evaluation/results.json'], EXPECTED_RESULTS)
    check('known_241_ledger', files['evaluation/queries.jsonl'], EXPECTED_LEDGER)
    check('inventory_lock', files['zip-inventory.json'], protocol['inventory_sha256'])
    check('manifest_lock', files['prepared/manifest.json'], load('prepared/progress.json')['manifest_sha256'])
    check('evaluator_lock', app / 'tools/evaluate_raw_smpd.py', protocol['evaluator_sha256'], True)
    for name, expected in protocol['source_sha256'].items():
        check('source:' + name, app / name, expected, True)
    for name, expected in load('dependency-lock.json')['source_sha256'].items():
        check('dependency:' + name, relocate(name, mappings), expected, True)
    for name, path in [('compnet', compnet), ('pklnet', pklnet)]:
        check('model:' + name, path, protocol['model_sha256'][name])
    for row in rows:
        check('original:' + row['sample'], relocate(row['original'], mappings), row['sha256'])
        if row.get('enrollment_feature_ok'):
            check('feature:' + row['sample'], relocate(row['enrollment_feature'], mappings), row['enrollment_feature_sha256'])
    errors = []
    prepared, download = load('prepared/progress.json'), load('SMPD.download.json')
    if not prepared.get('complete') or not download.get('complete') or not download.get('zip_crc_checked'):
        errors.append('Preparation/archive CRC verification is incomplete')
    if len({r['sample'] for r in rows}) != len(rows):
        errors.append('Duplicate manifest sample')
    expected_split = sorted((r['subject'], r['condition'], r['index'], r['identity'], r['enrollment'])
        for r in protocol['samples'])
    actual_split = sorted((r['subject'], r['condition'], r['index'], r['identity'], r['enrollment']) for r in rows)
    if actual_split != expected_split:
        errors.append('Manifest labels or enrollment split differ from frozen protocol')
    try:
        queries, total = validate_prefix(rows, report, files['evaluation/queries.jsonl'].read_bytes())
        if (len(rows), total, len(queries)) != (3677, 3217, 241):
            errors.append('Unexpected image/query/prefix counts')
        if report['protocol_sha256'] != digest(files['protocol.json']):
            errors.append('Result protocol hash mismatch')
        if report['archive_sha256'] != load('SMPD.download.json')['sha256']:
            errors.append('Result archive hash mismatch')
        if report['complete']:
            errors.append('Expected interrupted checkpoint')
    except (ValueError, KeyError) as error:
        errors.append(str(error))
    return dict(ready_for_parity_check=not errors and all(c['ok'] for c in checks),
        cross_host_resume_authorized=False, checks=checks, errors=errors,
        note='Successful audit permits a separately recorded parity pilot only; preserve the original 241 records.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--app', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--compnet', type=Path, required=True)
    p.add_argument('--pklnet', type=Path, required=True)
    p.add_argument('--map', action='append', default=[], dest='mappings')
    a = p.parse_args()
    result = audit(a.root, a.app, a.compnet, a.pklnet, [x.split('=', 1) for x in a.mappings])
    print(json.dumps(result, indent=2))
    return 0 if result['ready_for_parity_check'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
