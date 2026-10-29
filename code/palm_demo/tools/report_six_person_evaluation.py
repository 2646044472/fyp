"""Render the frozen six-person evaluation, keeping every main query visible."""
import argparse
from collections import defaultdict
import html
import json
from pathlib import Path
import numpy as np


def esc(value):return html.escape(str(value))
def seconds(value):return '—' if value is None else f'{value/1000:.3f}'
def table(headers,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+esc(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def summarize(trials):
    values=[t['ms'] for t in trials]
    return [f"{sum(t['correct'] for t in trials)}/{len(trials)}",
        f"{sum(t['correct'] and t['ms']<=2500 for t in trials)}/{len(trials)}",
        seconds(float(np.median(values))) if values else '—',seconds(max(values)) if values else '—']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();data=json.loads(args.evidence.read_text());protocol=data['protocol']
    complete=data.get('complete',False)
    state='已完成' if complete else ('已暂停，以下包含未完成分组' if data.get('paused_by_user') else '正在运行，以下为部分结果')
    chunks=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>六人本地数据完整流程实验</title>',
        '<style>body{font:16px/1.65 system-ui,sans-serif;max-width:1400px;margin:36px auto;padding:0 22px;color:#182637}h1{font-size:29px}h2{margin-top:32px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #d0d8e2;padding:8px;text-align:left;vertical-align:top}th{background:#edf2f8;white-space:nowrap}.scroll{overflow:auto}.notice{border-left:4px solid #b97216;padding:10px 16px;background:#fff7e8}code{overflow-wrap:anywhere}details{margin:18px 0}small{color:#526276}</style>',
        '<h1>六人本地数据：冻结版本完整流程与速度</h1>',
        '<p>2026-10-29 · 纯 Raspberry Pi 5 · 实验隔离环境 · '+state+'</p>',
        '<p class="notice">本次只做实验，不调整算法。120 张原图、6 个人员标签、11 个掌纹身份。此前开发实验的 80/80 不代表这六个人的结果；本页重新统计本次完整分母。</p>',
        '<p>冻结算法版本：<code>'+esc(protocol['frozen_commit'])+'</code>；匹配器：<code>'+esc(protocol['matcher'])+'</code>。协议保存了识别代码、模型与原图校验信息。参与者此前已被查看或测试，不作为未见身份验证。</p>',
        '<h2>数据与划分</h2>']
    chunks.append(table(['人员标签','原图数'],protocol['subject_images'].items()))
    chunks.append('<p>syr 的两次采集均按已确认的右手标签组成同一身份，保留 ZIP 原始标签与更正记录。正向组每个身份取最早 5 张注册，反向组取最晚 5 张；其余全部查询。每组 55 张注册、65 张查询，syr 每组查询 15 张，其余每个人查询 10 张。两组均从空库重新注册。</p>')
    chunks.append('<h2>主查询结果</h2><p>“正确”要求 HTTP 成功、返回 MATCH 且身份正确。“≤2.5 秒正确”还要求整个请求在 2500 毫秒内完成。错误、定位失败、注册失败影响的查询和超时均保留在分母。</p>')
    main_rows=[]
    for run in data['runs']:
        main_rows.append([run['case'],f"{len(run['queries'])}/65"]+summarize(run['queries'])+[
            sum(e['http_status']==200 for e in run['enrollments']),
            sum(e['result'].get('recognition_ready') is True for e in run['enrollments'])])
    chunks.append(table(['分组','查询进度','正确','≤2.5秒正确','中位秒（含错误）','最慢秒','已成功注册身份','已准备完成身份'],main_rows))
    chunks.append('<p>计时包含原图读取、预处理、ROI、特征、检索/配准、评分及本机 HTTP 返回；排除真实拍摄、摆手和外部上传。每次查询重新读取原图并计算，不缓存查询答案。查询时间不包含此前注册计算、服务启动和排队时间。</p>')
    for run in data['runs']:
        chunks.append('<h2>'+esc(run['case'])+'：逐人结果</h2>')
        people=defaultdict(list)
        for trial in run['queries']:people[trial['identity'].rsplit(':',1)[0]].append(trial)
        chunks.append(table(['人员标签','正确','≤2.5秒正确','中位秒','最慢秒'],[[person]+summarize(trials) for person,trials in sorted(people.items())]))
        chunks.append('<h2>'+esc(run['case'])+'：现场等价注册与立即首查</h2>')
        immediate={r['identity']:r for r in run['immediate_queries']};enrollment_rows=[]
        for entry in run['enrollments']:
            query=immediate.get(entry['identity']);events=entry['events']
            stage=lambda label:sum(e['ms'] for e in events if e['stage']==label)
            enrollment_rows.append([entry['identity'],entry['http_status'],entry['result'].get('recognition_ready'),
                seconds(entry['ms']),seconds(entry.get('last_frame_read_to_response_ms')),
                seconds(stage('primary_roi')),seconds(stage('alternate_roi')),seconds(stage('complete_features')),
                seconds(stage('template_save')),seconds(stage('prepare_enrollment')),seconds(stage('descriptor_index')),
                seconds(stage('index_and_enrollment_links')),seconds(query['ms']) if query else '—',query['correct'] if query else '—'])
        chunks.append(table(['身份','注册HTTP','ready','注册总秒','末帧读取后秒','主ROI秒','备用ROI秒','完整特征秒','保存秒','模板准备秒','全库索引秒','索引+对齐秒','立即首查秒','首查正确'],enrollment_rows))
        chunks.append('<p>各阶段存在嵌套和并行，不能相加。“末帧读取后秒”是文件回放中的最后一张图读取结束到 HTTP 返回，不是实测相机最后一帧到 ready。注册总时间包含逐张处理，真实拍摄尚未测量。额外立即首查单列，不计入主查询的 65 次结果。</p>')
        startup=run['startup'];restart=run.get('restart')
        chunks.append('<p>本组通用模型启动 '+seconds(startup['generic_model_startup_ms'])+' 秒；空库应用初始化 '+seconds(startup['app_and_gallery_ms'])+' 秒。模型只用全零输入预热。</p>')
        if restart:
            chunks.append('<p>独立新进程重新加载已注册图库：模型启动 '+seconds(restart['startup']['generic_model_startup_ms'])+' 秒，应用/图库重建 '+seconds(restart['startup']['app_and_gallery_ms'])+' 秒；首次查询 '+seconds(restart['first_query']['ms'])+' 秒，正确='+esc(restart['first_query']['correct'])+'。这是进程重启，不是树莓派重启。</p>')
        if run.get('summary'):
            chunks.append('<p>模拟支付新增交易数：'+esc(run['summary']['payment_transactions'])+'；所有身份的确认、重复确认拦截、取消及取消后确认检查均通过：'+esc(run['summary']['payment_checks_complete'])+'。</p>')
        checks=run['payment_checks']
        if checks:chunks.append(table(['身份','确认','重复确认拦截','取消','取消后确认拦截'],[[u]+[checks[u].get(k,'未覆盖') for k in ('confirmed','duplicate_blocked','cancelled','cancelled_confirmation_blocked')] for u in sorted(checks)]))
        chunks.append('<h2>'+esc(run['case'])+'：全部主查询（耗时降序）</h2>')
        chunks.append(table(['样本','真实身份','返回身份','正确','≤2.5秒正确','秒','HTTP','状态','最佳分数','第二分数','路径'],[
            [r['sample'],r['identity'],r['result'].get('user_id','—'),r['correct'],r['correct'] and r['ms']<=2500,
             seconds(r['ms']),r['http_status'],r['result'].get('status',r['result'].get('message','—')),
             r['result'].get('score','—'),r['result'].get('second_score','—'),r['result'].get('recognition_route','—')]
            for r in sorted(run['queries'],key=lambda r:r['ms'],reverse=True)]))
    samples=data['power_samples'];flags=sorted({s.get('get_throttled','unknown') for s in samples})
    chunks.append('<h2>完整性与边界</h2><p>功耗/温度采样 '+str(len(samples))+' 次；观测到的电源/降频标志：'+esc(', '.join(flags))+'。原图复核未变：'+esc(data.get('originals_unchanged','等待最终复核'))+'。</p>')
    chunks.append('<p>这是已暴露的本地旧相机数据上的闭集识别测试，不能证明 40 人容量、跨设备、独立新会话或陌生人拒识能力。现有模拟 demo 最终采用闭集排序策略；提前返回门槛用于选择计算路径，不等于已完成拒识校准。算法参数未根据本次结果改变。</p>')
    chunks.append('<p><small>原始结果：'+esc(args.evidence.name)+'。原图及模板保存在本地隔离目录，未纳入代码提交。</small></p></html>')
    args.output.write_text(''.join(chunks),encoding='utf-8')
    print(json.dumps(dict(complete=complete,runs=main_rows),ensure_ascii=False))


if __name__=='__main__':main()
