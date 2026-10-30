"""One-shot completion dependency for the currently running SMPD experiment.

Does not start inference, change its sources, retry failures, publish data,
schedule future experiments or send messages. Saves periodic private snapshots
and exports reviewable scalar reports only after a verified complete result.
"""
import argparse
import json
import time
from pathlib import Path

import psutil
from report_raw_smpd import build_summary, write_scalars, render_html, write_markdown


def save(path, value):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2),encoding='utf-8');temp.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--inference-pid',required=True,type=int);p.add_argument('--final-scalars',required=True,type=Path)
    a=p.parse_args();process=psutil.Process(a.inference_pid);created=process.create_time()
    assert any(name in ' '.join(process.cmdline()) for name in ('run_locked_smpd.py','resume_raw_smpd.py'))
    previous=-1;rendered=0
    while True:
        file=a.root/'evaluation/results.json'
        result=json.loads(file.read_text(encoding='utf-8')) if file.exists() else None
        count=len(result['queries']) if result else 0
        try:
            alive=process.is_running() and process.create_time()==created
            rss=process.memory_info().rss if alive else None
        except psutil.NoSuchProcess:
            alive=False;rss=None
        status=dict(complete=False,inference_pid=a.inference_pid,process_alive=alive,queries=count,expected_queries=3217,
            inference_rss_bytes=rss,updated_at_unix=time.time())
        if result and result['complete']:
            summary,rows,queries=build_summary(a.root)
            write_scalars(a.final_scalars,summary,rows,queries)
            write_markdown(a.final_scalars/'RESULTS.md',summary)
            render_html(a.root,summary,rows,queries)
            status.update(complete=True,final_scalar_output=str(a.final_scalars.resolve()),summary=summary['overall'])
            save(a.root/'report-follow-status.json',status)
            print(json.dumps(status),flush=True);return
        if not alive:
            status['failure']='Inference process exited before a verified complete result; preserve partial evidence. No automatic restart.'
            save(a.root/'report-follow-status.json',status)
            raise RuntimeError(status['failure'])
        if result and time.monotonic()-rendered>=300:
            summary,rows,queries=build_summary(a.root,partial=True)
            write_scalars(a.root/'report-scalars',summary,rows,queries)
            write_markdown(a.root/'report-scalars/RESULTS.md',summary)
            render_html(a.root,summary,rows,queries);rendered=time.monotonic()
        save(a.root/'report-follow-status.json',status)
        if count!=previous:
            print('full-run-progress',count,'/3217',flush=True);previous=count
        time.sleep(20)


if __name__=='__main__':main()
