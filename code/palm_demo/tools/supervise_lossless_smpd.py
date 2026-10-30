"""One frozen v27 run: verify two formal queries, continue at3, no crash retry.

Reuse the prior tested supervisor policy, with explicit v27 runner/report globals
and exact supplemental source lock. This creates no recurring experiment.
"""
import argparse
import inspect
from pathlib import Path
import types

import supervise_terminal_smpd as previous
import run_lossless_smpd as run
from report_lossless_smpd import report


def functions():
    namespace=dict(vars(previous),__file__=__file__,run=run,report=report)
    for name in ('seal','validate_lock','validate_preflight'):
        source=inspect.getsource(getattr(previous,name))
        source=source.replace('report_terminal_smpd','report_lossless_smpd')
        exec(compile(source,'<v27-frozen-supervisor-'+name+'>','exec'),namespace)
    for name in ('alive','watch'):
        namespace[name]=types.FunctionType(getattr(previous,name).__code__,namespace,name)
    return namespace


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('seal','watch'));parser.add_argument('root',type=Path)
    args=parser.parse_args();root=args.root.resolve();namespace=functions()
    if args.mode=='seal':(root/'supervision').mkdir(exist_ok=True)
    namespace[args.mode](root)
