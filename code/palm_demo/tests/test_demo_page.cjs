const fs = require('fs'), vm = require('vm'), assert = require('assert');
const script = fs.readFileSync(require('path').join(__dirname, '../demo_page.py'), 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const flush = () => new Promise(resolve => setImmediate(resolve));

function page(storage = new Map()) {
  const elements = new Map(), timers = new Map(), calls = [], actions = [], frames = [], created = [], revoked = [];
  let now = 0, nextTimer = 0, loadImages = true;
  let roiStatus = {camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5};
  let statusFailure = false;
  const element = id => {
    if (!elements.has(id)) {
      const node = {value: '', hidden: ['live', 'roi', 'candidate', 'enroll-restore'].includes(id), disabled: false, textContent: '', _src: '', onload: null, onerror: null,
        removeAttribute(name) { if (name === 'src') this._src = ''; }};
      Object.defineProperty(node, 'src', {get() { return this._src; }, set(value) {
        this._src = value;
        if (id === 'live' && loadImages) { const onload = this.onload; queueMicrotask(() => { if (onload) onload(); }); }
      }});
      elements.set(id, node);
    }
    return elements.get(id);
  };
  const setTimer = (fn, ms, interval = false) => {
    timers.set(++nextTimer, {fn, due: now + ms, interval: interval ? ms : 0}); return nextTimer;
  };
  const context = {
    document: {getElementById: element}, AbortController, console, Date: {now: () => now},
    sessionStorage: {getItem: key => storage.get(key) ?? null, setItem: (key, value) => { if (storage.failSet) throw Error('SecurityError'); storage.set(key, String(value)); }, removeItem: key => storage.delete(key)},
    URL: {createObjectURL: () => { const url = 'blob:preview-' + (created.length + 1); created.push(url); return url; }, revokeObjectURL: url => revoked.push(url)},
    setTimeout: (fn, ms) => setTimer(fn, ms), clearTimeout: id => timers.delete(id),
    setInterval: (fn, ms) => setTimer(fn, ms, true), clearInterval: id => timers.delete(id),
    fetch(path, options) {
      if (path.startsWith('/frame.jpg')) return new Promise((resolve, reject) => frames.push({path, options, resolve, reject}));
      if (path === '/api/demo/users') return Promise.resolve({ok: true, json: async () => ({users: []})});
      if (path.startsWith('/api/status')) return Promise.resolve({ok: !statusFailure, json: async () => roiStatus});
      if (path === '/api/camera/focus' && !options) return Promise.resolve({ok: true, json: async () => ({supported: false})});
      calls.push({path, payload: JSON.parse(options.body)});
      return new Promise((resolve, reject) => actions.push({resolve, reject}));
    }
  };
  vm.createContext(context); vm.runInContext(script, context);
  return {
    element, calls, actions, frames, created, revoked, context, storage,
    setImageLoading(value) { loadImages = value; },
    finish(data) { actions.shift().resolve({ok: true, json: async () => data}); },
    async frame(index, ok = true) { frames[index].resolve({ok, status: ok ? 200 : 503, blob: async () => ({})}); await flush(); },
    setStatus(value) { roiStatus = value; },
    failStatus(value) { statusFailure = value; },
    async refreshStatus() { await context.pollStatus(); await flush(); },
    async ready() {
      await this.frame(0);
      this.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
      await this.refreshStatus();
      assert(!element('identify').disabled);
    },
    async advance(ms) {
      const end = now + ms;
      for (;;) {
        const due = [...timers.entries()].filter(([, t]) => t.due <= end).sort((a, b) => a[1].due - b[1].due || a[0] - b[0])[0];
        if (!due) break;
        const [id, timer] = due; now = timer.due;
        if (timer.interval) timer.due += timer.interval; else timers.delete(id);
        timer.fn(); await flush();
      }
      now = end; await flush();
    },
    intervalCount() { return [...timers.values()].filter(t => t.interval).length; }
  };
}
async function identify(p, token = 'one') {
  const run = p.element('identify').onclick();
  p.finish({status: 'MATCH', token, user_id: 'p1', display_name: 'P1', score: .2, second_score: .3}); await run;
}
(async () => {
  {
    const p = page();
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    await p.element('identify').onclick(); assert.equal(p.calls.length, 0);
    p.setImageLoading(false); await p.frame(0);
    assert(p.element('identify').disabled, 'a received image must be displayed before enabling capture');
    p.element('live').onload(); await flush();
    assert(!p.element('live').hidden && p.element('identify').disabled && p.element('enroll').disabled,
      'a fresh preview without a ready palm must keep capture actions disabled');
    assert(p.element('roi-status').textContent.includes('NO_HAND'));
    await p.element('identify').onclick(); await p.element('enroll').onclick();
    assert.equal(p.calls.length, 0, 'no-hand actions must not reach enrollment or identification routes');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 4, quality_required_frames: 5});
    await p.refreshStatus();
    assert(p.element('identify').disabled, 'ROI must meet the full consecutive-frame requirement');
    p.setStatus({camera_ready: true, roi_status_fresh: false, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert(p.element('identify').disabled, 'a stale READY ROI must not enable capture');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert(!p.element('live').hidden && !p.element('identify').disabled);
    p.failStatus(true); await p.refreshStatus();
    assert(p.element('identify').disabled && p.element('enroll').disabled,
      'a failed readiness poll must block capture actions');
    assert(p.element('roi-status').textContent.includes('状态不可用'));
    p.failStatus(false); await p.refreshStatus();
    assert(!p.element('identify').disabled);
    assert(p.element('camera-status').textContent.includes('已连接'));
    await p.advance(300); await p.context.preview();
    assert.equal(p.frames.length, 2, 'an active preview request must not overlap another poll');
    await p.frame(1, false);
    assert(p.element('live').hidden && !p.element('live').src);
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    assert(p.element('camera-status').textContent.includes('不可用'));
    assert(p.revoked.includes('blob:preview-1'));
    p.setImageLoading(true); await p.advance(300); await p.frame(2);
    await p.refreshStatus();
    assert(!p.element('live').hidden && !p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    p.setStatus({camera_ready: true, roi_status_fresh: true,
      quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5,
      demo_quality_status: 'LOW_QUALITY', demo_quality_reason: 'sharpness_below_minimum',
      demo_quality_consecutive_frames: 0, demo_quality_required_frames: 5});
    await p.refreshStatus();
    assert(p.element('identify').disabled && p.element('enroll').disabled,
      'diagnostic READY must not enable actions when demo sharpness is below its floor');
    assert(p.element('roi-status').textContent.includes('偏模糊'));
    await p.element('identify').onclick(); await p.element('enroll').onclick();
    assert.equal(p.calls.length, 0);
    p.setStatus({camera_ready: true, roi_status_fresh: true,
      quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5,
      demo_quality_status: 'READY', demo_quality_consecutive_frames: 5, demo_quality_required_frames: 5});
    await p.refreshStatus();
    assert(!p.element('identify').disabled && !p.element('enroll').disabled);
  }
  {
    const p = page(); await p.ready(); await p.advance(5000);
    assert(p.element('live').hidden && !p.element('live').src);
    assert(p.element('identify').disabled && p.element('camera-status').textContent.includes('停止更新'));
    await p.advance(300);
    assert(p.frames[1].options.signal.aborted, 'a hung request must be aborted within the preview deadline');
    await p.advance(300); await p.frame(2);
    const fresh = p.element('live').src;
    await p.frame(1); // A transport can finish after its AbortSignal fired.
    assert.equal(p.element('live').src, fresh, 'a late expired response must not replace the recovered preview');
    assert.equal(p.created.length, 2); await p.refreshStatus(); assert(!p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    let run = p.element('identify').onclick(); await p.element('identify').onclick(); await p.element('retry').onclick();
    assert.equal(p.calls.length, 1); assert(p.element('retry').disabled && p.element('user').disabled);
    await p.advance(1000); assert(p.element('notice').textContent.includes('秒'));
    await p.frame(1, false); p.finish({status: 'UNKNOWN'}); await run;
    assert.equal(p.intervalCount(), 0);
    assert(p.element('identify').disabled, 'finishing an action must not re-enable capture after camera loss');
    await p.advance(300); await p.frame(2); await p.refreshStatus();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    run = p.element('enroll').onclick(); await flush(); await p.element('enroll').onclick();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/start').length, 1);
    p.finish({token: 'burst', max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    for (let kept = 1; kept <= 8; kept++) {
      assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
      p.finish({status: kept === 8 ? 'READY' : 'COLLECTING', kept: kept === 8 ? 5 : 0,
        candidate_pool_count: kept, candidate_pool_required: 8, required: 5, attempts: kept,
        selected_roi_images: kept === 8 ? ['one','two','three','four','five'] : undefined}); await flush();
    }
    await run;
    assert(p.element('enroll-progress').textContent.includes('5/5'));
    assert(!p.element('enroll-commit').hidden);
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    assert(!p.element('enroll-cancel').disabled);
    const commit = p.element('enroll-commit').onclick();
    assert.equal(p.calls.at(-1).payload.confirm_hand, 'left');
    p.finish({display_name: 'P1', balance_cents: 10000}); await commit;
    assert(!p.element('user').disabled && !p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    p.finish({token: 'repeat', max_quality_failures: 15}); await flush();
    p.finish({status: 'KEPT', kept: 1, required: 5, attempts: 1, duplicate_frames: 0, quality_failures: 0}); await flush();
    p.finish({status: 'WAIT', kept: 1, required: 5, attempts: 17, duplicate_frames: 16,
              quality_failures: 0, retry_after_ms: 700, reason: '请移动手掌'}); await flush();
    assert(p.element('enroll-progress').textContent.includes('重复跳过 16 张'));
    assert(p.element('notice').textContent.includes('移动手掌'));
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    const cancel = p.element('enroll-cancel').onclick();
    assert(p.element('notice').textContent.includes('正在取消'));
    p.finish({status: 'CANCELLED'}); await cancel;
    await p.advance(700); await run;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    assert(!p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const start = p.element('enroll').onclick(); await flush();
    p.finish({token: 'recover', max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
    p.actions.shift().reject(Error('temporary connection loss')); await start;
    assert(!p.element('enroll-resume').hidden && !p.element('enroll-resume').disabled,
      'a failed step must leave the same enrollment resumable');
    const retry = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.at(-1).payload.token, 'recover');
    p.actions.shift().reject(Error('temporary connection loss')); await retry;
    assert(!p.element('enroll-resume').hidden && !p.element('enroll-resume').disabled,
      'a failed resume must remain retryable');
    const recovered = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.at(-1).payload.token, 'recover');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 1, quality_failures: 0,
      capture_failure: 'NO_HAND', reason: '持续采集已暂停'}); await recovered;
    assert(!p.element('enroll-resume').hidden);
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(p.element('enroll-resume').hidden);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    p.finish({token: 'camera-recovery', max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    p.finish({status: 'WAIT', kept: 1, required: 5, attempts: 3, duplicate_frames: 1,
      quality_failures: 0, candidate_pool_count: 2, candidate_pool_required: 8,
      capture_failure: 'CAMERA_UNAVAILABLE', retry_after_ms: 500,
      reason: '暂时无法读取相机画面，请检查连接后重试。'}); await run;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'camera loss pauses automatic steps instead of retrying every 500 ms');
    assert(p.element('enroll-resume').hidden === false);
    assert(p.element('enroll-progress').textContent.includes('候选 2/8'),
      'candidate-pool progress is retained while paused');
    assert(p.element('notice').textContent.includes('录入已暂停'));
    await p.advance(2000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'no repeated capture request is made while camera recovery is pending');
    p.setStatus({camera_ready: false, roi_status_fresh: false, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'fresh camera/ROI readiness resumes the same session once');
    assert.equal(p.calls.at(-1).payload.token, 'camera-recovery');
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'repeated READY polls do not launch parallel enrollment loops');
    p.finish({status: 'WAIT', kept: 1, required: 5, attempts: 4, candidate_pool_count: 2,
      candidate_pool_required: 8, capture_failure: 'NO_HAND', reason: '持续采集已暂停'}); await flush();
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    p.finish({token: 'no-hand', max_quality_failures: 15}); await flush();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 1, duplicate_frames: 0,
      quality_failures: 0, capture_failure: 'NO_HAND', resume_required: true,
      reason: '未检测到手掌，自动采集已暂停。请把手掌放入画面并等掌区就绪后点击“继续采集”，也可取消。'}); await flush();
    assert(p.element('notice').textContent.includes('已暂停'));
    assert(p.element('enroll-progress').textContent.includes('质量重试 0/15'));
    assert(!p.element('enroll-resume').hidden && p.element('enroll-resume').disabled,
      'paused no-hand state should expose resume but keep it disabled until ROI is ready');
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'no-hand must stop automatic enrollment requests');
    await p.refreshStatus();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'fresh READY automatically resumes the same enrollment token');
    assert(p.element('enroll-resume').disabled, 'the manual fallback is disabled while automatic resume is running');
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'subsequent READY polls do not create a parallel step loop');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 2, quality_failures: 0,
      capture_failure: 'NO_HAND', resume_required: true, reason: '持续采集已暂停'}); await flush();
    await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a NO_HAND high-resolution capture while preview remains READY does not auto-loop');
    assert(!p.element('enroll-resume').disabled,
      'manual resume stays available after the preview reports READY again');
    const resume = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'manual resume can continue after a preview/high-resolution mismatch');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 3, quality_failures: 0,
      capture_failure: 'NO_HAND', resume_required: true, reason: '持续采集已暂停'}); await flush();
    await resume;
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel; await run;
    assert(p.element('enroll-resume').hidden, 'cancel clears the paused resume control');
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); await p.element('confirm').onclick(); await p.element('retry').onclick();
    assert.equal(p.calls.length, 2); p.actions.shift().reject(Error('lost confirmation response')); await run;
    assert(p.element('notice').textContent.includes('状态待核实'));
    assert(!p.element('notice').textContent.includes('没有扣款'));
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    await p.element('identify').onclick(); await p.element('enroll').onclick();
    assert.equal(p.calls.length, 2, 'uncertain confirmation must preserve its token and block new capture actions');
    assert(!p.element('confirm').disabled && !p.element('retry').disabled);
    run = p.element('retry').onclick();
    p.finish({status: 'PAID', payment_status: 'SUCCESS', display_name: 'P1', balance_cents: 8000, amount_cents: 2000}); await run;
    assert(p.element('candidate').hidden);
    assert(p.element('notice').textContent.includes('模拟支付成功') && p.element('notice').textContent.includes('80.00'));
    assert(!p.element('notice').textContent.includes('没有扣款')); assert(!p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready(); await identify(p, 'retry-confirm');
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('confirm').onclick(); assert.equal(p.calls.at(-1).payload.token, 'retry-confirm');
    p.finish({status: 'SUCCESS', display_name: 'P1', amount_cents: 2000, balance_cents: 8000}); await run;
    assert(p.element('notice').textContent.includes('模拟支付成功'));
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('retry').onclick();
    p.finish({status: 'PAID', payment_status: 'INSUFFICIENT_BALANCE', display_name: 'P1', balance_cents: 1000}); await run;
    assert(p.element('notice').textContent.includes('余额不足') && p.element('notice').textContent.includes('没有扣款'));
    assert(!p.element('notice').textContent.includes('支付成功'));
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('retry').onclick(); p.finish({status: 'UNCONFIRMED'}); await run;
    assert(p.element('identify').disabled && !p.element('candidate').hidden);
    assert(!p.element('notice').textContent.includes('没有扣款'));
    run = p.element('retry').onclick(); p.finish({status: 'CANCELLED'}); await run;
    assert(p.element('candidate').hidden && !p.element('identify').disabled);
    assert(p.element('notice').textContent.includes('没有扣款'));
  }
  {
    const storage = new Map(), first = page(storage); await first.ready();
    first.element('user').value = 'p1_left'; first.element('name').value = 'P1'; first.element('hand').value = 'left';
    const enrollment = first.element('enroll').onclick(); await flush();
    first.finish({token: 'refresh-ready', max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    first.finish({status: 'READY', kept: 5, required: 5, attempts: 8, quality_failures: 0,
      candidate_pool_count: 8, candidate_pool_required: 8, selected_roi_images: ['a','b','c','d','e']});
    await enrollment;
    assert.equal(storage.get('palm_demo_enrollment_token'), 'refresh-ready');

    const refreshed = page(storage); await flush();
    assert.equal(refreshed.calls[0].path, '/api/demo/enroll/status');
    assert.equal(refreshed.calls[0].payload.token, 'refresh-ready');
    refreshed.finish({status: 'READY', user_id: 'p1_left', display_name: 'P1', hand: 'left', kept: 5,
      required: 5, attempts: 8, quality_failures: 0, duplicate_frames: 0, candidate_pool_count: 8,
      candidate_pool_required: 8, max_quality_failures: 15, selected_roi_images: ['a','b','c','d','e']});
    await flush();
    assert.equal(refreshed.element('user').value, 'p1_left');
    assert.equal(refreshed.element('hand').value, 'left');
    assert(!refreshed.element('enroll-commit').hidden, 'a READY session restores the confirm action');
    assert(refreshed.element('enroll-thumbs').innerHTML.includes('data:image/png;base64,e'));
    const cancel = refreshed.element('enroll-cancel').onclick();
    refreshed.finish({status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token'), 'cancel removes the refresh token');
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'refresh-partial']]), p = page(storage); await flush();
    p.finish({status: 'PAUSED', user_id: 'p2_left', display_name: 'P2', hand: 'left', kept: 0, required: 5,
      attempts: 2, quality_failures: 0, duplicate_frames: 0, candidate_pool_count: 2,
      candidate_pool_required: 8, max_quality_failures: 15, selected_roi_images: []}); await flush();
    assert(!p.element('enroll-resume').hidden, 'a partial session restores a manual continuation control');
    await p.frame(0);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
    assert.equal(p.calls.at(-1).payload.token, 'refresh-partial');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 3, quality_failures: 0,
      capture_failure: 'NO_HAND', resume_required: true, reason: '持续采集已暂停'}); await flush();
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token'));
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'expired-token']]), p = page(storage); await flush();
    p.finish({status: 'EXPIRED'}); await flush();
    assert(!storage.has('palm_demo_enrollment_token'));
    assert(p.element('notice').textContent.includes('超时'));
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'temporary-network-token']]), p = page(storage); await flush();
    p.actions.shift().reject(Error('temporary network loss')); await flush();
    assert.equal(storage.get('palm_demo_enrollment_token'), 'temporary-network-token',
      'a temporary status query failure must preserve the only session token');
    assert(!p.element('enroll-restore').hidden, 'the page exposes an explicit status retry');
    assert(!p.element('enroll-cancel').hidden, 'the still-unknown server session can be cancelled');
    assert(p.element('enroll-resume').hidden, 'capture cannot resume until session state is confirmed');
    assert(p.element('notice').textContent.includes('token 已保留'));
    const retry = p.element('enroll-restore').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status');
    assert.equal(p.calls.at(-1).payload.token, 'temporary-network-token');
    p.finish({status: 'PAUSED', user_id: 'p4_left', display_name: 'P4', hand: 'left', kept: 1, required: 5,
      attempts: 3, quality_failures: 0, duplicate_frames: 1, candidate_pool_count: 2,
      candidate_pool_required: 8, max_quality_failures: 15, selected_roi_images: ['a']});
    await retry;
    assert.equal(p.element('user').value, 'p4_left');
    assert(!p.element('enroll-resume').hidden, 'a confirmed partial session restores its existing controls');
    assert(p.element('enroll-restore').hidden);
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token'));
  }
  {
    const storage = new Map(); storage.failSet = true;
    const p = page(storage); await p.ready();
    p.element('user').value = 'p3_left'; p.element('name').value = 'P3'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finish({token: 'storage-denied', max_quality_failures: 15}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/cancel', 'failed token persistence immediately cancels the server session');
    assert.equal(p.calls.at(-1).payload.token, 'storage-denied');
    p.finish({status: 'CANCELLED'}); await enrollment;
    assert(p.element('notice').textContent.includes('已取消'));
    assert(p.element('enroll-cancel').hidden && p.element('enroll-resume').hidden);
  }
  console.log('UI interaction checks passed: preview freshness, disconnect/recovery, enrollment refresh recovery, timeouts and late responses, busy controls, and payment confirmation recovery.');
})().catch(error => { console.error(error); process.exitCode = 1; });
