#!/usr/bin/env python3
"""Local experiment control index. Never executes experiments or modifies run artifacts."""
import re
from collections import defaultdict

STATES = {'unreviewed', 'planned', 'running', 'completed', 'blocked', 'invalidated', 'superseded'}
ID = re.compile(r'-D(\d+)(?:-|$)', re.I)


def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported registry schema')
    rows = data['experiments']
    by_id = {row['id']: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError('Duplicate experiment ID')
    for row in rows:
        if not re.fullmatch(r'D\d+', row['id']):
            raise ValueError('Invalid experiment ID')
        if row['candidate_status'] not in STATES:
            raise ValueError('Unknown candidate status')
        for edge in row.get('dependencies', []):
            if edge['id'] not in by_id:
                raise ValueError(f"Missing dependency: {edge['id']}")
            if not isinstance(edge['propagates_invalidation'], bool):
                raise ValueError('Dependency requires explicit invalidation semantics')
    visiting, visited = set(), set()
    def walk(key):
        if key in visiting:
            raise ValueError('Dependency cycle')
        if key in visited:
            return
        visiting.add(key)
        for edge in by_id[key].get('dependencies', []):
            walk(edge['id'])
        visiting.remove(key)
        visited.add(key)
    for key in by_id:
        walk(key)
    return by_id


def invalidation_sources(key, by_id):
    """Only candidate-artifact edges propagate. Historical protocol references do not."""
    found = set()
    def walk(node):
        if by_id[node]['candidate_status'] == 'invalidated':
            found.add(node)
        for edge in by_id[node].get('dependencies', []):
            if edge['propagates_invalidation']:
                walk(edge['id'])
    walk(key)
    return sorted(found, key=lambda x: int(x[1:]))


def inventory(runtime):
    """Inspect immediate directory names and report names only, never biometric contents."""
    result = defaultdict(list)
    for path in sorted(runtime.iterdir()):
        if path.is_symlink() or not path.is_dir():
            continue
        match = ID.search(path.name)
        if match:
            result[f'D{int(match.group(1))}'].append(path.name)
    return dict(result)


def render(data, runs):
    by_id = validate(data)
    ids = sorted(set(runs) | set(by_id), key=lambda x: int(x[1:]))
    lines = ['# Experiment registry (local review index)', '',
        f"Status reviewed: {data['reviewed_at']}. Directory presence alone does not establish completion or validity.", '',
        'Candidate status applies only to the specified arm. An invalid candidate does not invalidate the historical RTM, PKLNet or reference baseline.',
        'Historical artifacts remain in place. Do not cite results from an unreviewed directory.', '',
        '| ID | Candidate status | Invalidated dependencies | Purpose / current conclusion |',
        '| --- | --- | --- | --- |']
    for key in ids:
        row = by_id.get(key)
        if row:
            bad = ', '.join(invalidation_sources(key, by_id)) or '—'
            text = row['title'] + '; ' + row['decision']
            state = row['candidate_status']
        else:
            bad, text, state = '—', 'Directory listed; not yet reviewed', 'unreviewed'
        lines.append(f'| {key} | {state} | {bad} | {text.replace("|", "/")} |')
    lines += ['', '## Run directories', '',
        'A D identifier may have multiple attempts. The newest is not automatically authoritative. See the evidence field in registry.json for reviewed entries.', '']
    for key in ids:
        lines.append(f'### {key}')
        for name in runs.get(key, []):
            lines.append(f'- [{name}](../code/rasp/runtime/{name}/)')
        if key not in runs:
            lines.append('- No matching top-level run directory was found in this inventory. Check the source report.')
        row = by_id.get(key)
        if row:
            for source in row.get('evidence', []):
                lines.append(f'- Status evidence: [report](../{source})')
        lines.append('')
    return '\n'.join(lines)
