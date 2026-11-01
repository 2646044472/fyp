"""Private input binding for the published half-turn pilot drivers.

No image selection is distributed with these scripts. Importing them never
starts inference. A separate, explicitly authorized local manifest is needed.
"""
import json
import hashlib
from pathlib import Path
import re


def bind(kind, args):
    app = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    parent, child = args.parent.resolve(), args.continuation.resolve()
    geometry = args.geometry.resolve() if kind == 'identification' else None
    selection_path = args.selection.resolve()
    # All writes go beneath output, so reject ancestor/descendant aliases.
    for protected in [app, parent, child, geometry, selection_path.parent]:
        if protected is None:
            continue
        if output == protected or protected.is_relative_to(output):
            raise ValueError('Output would contain a protected source')
        if protected != app and output.is_relative_to(protected):
            raise ValueError('Output must be a separate directory')
    if not parent.is_dir() or not child.is_dir():
        raise ValueError('Frozen input directories must already exist')
    if not output.is_dir():
        raise ValueError('Create a separate output directory for fixture receipts first')
    value = json.loads(selection_path.read_text(encoding='utf-8'))
    result = dict(APP=app, PARENT=parent, CHILD=child,
                  SELECTION_PATH=selection_path)
    if kind == 'geometry':
        samples = value['samples']
        if len(samples) != 8 or value['negative'] != samples[-1]:
            raise ValueError('Expected eight ordered geometry samples, negative last')
        result.update(HERE=output, SAMPLES=samples, NEGATIVE=value['negative'])
    else:
        enrollment, queries = value['enrollment'], value['queries']
        if (len(enrollment) != 5 or len(queries) != 8
                or value['controls'] != queries[5:7]
                or value['recovered_enrollment'] not in enrollment):
            raise ValueError('Expected five enrollment, five target, two control, one negative')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', value['candidate_user']):
            raise ValueError('Unsafe candidate user identifier')
        samples = enrollment + queries
        result.update(ROOT=output, GEOMETRY=geometry, ENROLL=enrollment,
                      QUERIES=queries, CONTROLS=value['controls'],
                      CANDIDATE_USER=value['candidate_user'],
                      RECOVERED_ENROLLMENT=value['recovered_enrollment'])
    if (len(set(samples)) != len(samples)
            or any(not re.fullmatch(r'[A-Za-z0-9_-]+', s) for s in samples)):
        raise ValueError('Sample identifiers must be distinct safe filename components')
    result['BINDING'] = dict(kind=kind, output=str(output), parent=str(parent),
                            continuation=str(child), geometry=str(geometry),
                            selection=str(selection_path),
                            selection_sha256=hashlib.sha256(selection_path.read_bytes()).hexdigest())
    return result


def arguments(parser, kind):
    parser.add_argument('mode', choices=['prepare', 'run'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--continuation', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True,
                        help='Local private selection JSON; never commit it')
    if kind == 'identification':
        parser.add_argument('--geometry', type=Path, required=True)
    return parser
