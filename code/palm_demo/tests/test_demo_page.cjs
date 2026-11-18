const fs = require('fs'), vm = require('vm'), assert = require('assert');
const script = fs.readFileSync(require('path').join(__dirname, '../demo_page.py'), 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const flush = () => new Promise(resolve => setImmediate(resolve));
const watchdog = setTimeout(() => { console.error('UI interaction test did not finish'); process.exit(1); }, 15000);

function page(storage = new Map(), gate = false) {
  const elements = new Map(), timers = new Map(), calls = [], actions = [], frames = [], statusRequests = [], created = [], revoked = [];
  let now = 0, nextTimer = 0, loadImages = true, randomTokenByte = 0;
  let roiStatus = {camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5};
  let statusFailure = false, hangNextStatus = false;
  const element = id => {
    if (!elements.has(id)) {
      const node = {value: '', hidden: ['live', 'roi', 'candidate', 'enroll-restore'].includes(id), disabled: false, textContent: '', style: {}, naturalWidth: 640, naturalHeight: 360, _src: '', onload: null, onerror: null,
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
  element('users').parentElement = {children: []};
  const context = {
    document: {getElementById: element, querySelector: () => ({})}, AbortController, URLSearchParams, location: {search: gate ? '?mode=gate' : ''}, console, Date: {now: () => now}, performance: {now: () => now},
    crypto: {getRandomValues(bytes) { bytes.fill(0); bytes[15] = ++randomTokenByte; return bytes; }},
    sessionStorage: {getItem: key => storage.get(key) ?? null, setItem: (key, value) => { if (storage.failSet) throw Error('SecurityError'); storage.set(key, String(value)); }, removeItem: key => storage.delete(key)},
    URL: {createObjectURL: () => { const url = 'blob:preview-' + (created.length + 1); created.push(url); return url; }, revokeObjectURL: url => revoked.push(url)},
    setTimeout: (fn, ms) => setTimer(fn, ms), clearTimeout: id => timers.delete(id),
    setInterval: (fn, ms) => setTimer(fn, ms, true), clearInterval: id => timers.delete(id),
    fetch(path, options) {
      if (path.startsWith('/frame.jpg')) return new Promise((resolve, reject) => frames.push({path, options, resolve, reject}));
      if (path === '/api/demo/users') return Promise.resolve({ok: true, json: async () => ({users: []})});
      if (path.startsWith('/api/status')) return new Promise(resolve => {
        const request = {options, resolve: (value = roiStatus, ok = !statusFailure) => resolve({ok, json: async () => value})};
        statusRequests.push(request);
        if (!hangNextStatus) request.resolve();
        hangNextStatus = false;
      });
      if (path === '/api/camera/focus' && !options) return Promise.resolve({ok: true, json: async () => ({supported: false})});
      calls.push({path, payload: JSON.parse(options.body)});
      return new Promise((resolve, reject) => actions.push({resolve, reject}));
    }
  };
  vm.createContext(context); vm.runInContext(script, context);
  return {
    element, calls, actions, frames, statusRequests, created, revoked, context, storage,
    setImageLoading(value) { loadImages = value; },
    setImageSize(width, height) { element('live').naturalWidth = width; element('live').naturalHeight = height; },
    finish(data) { actions.shift().resolve({ok: true, json: async () => data}); },
    finishAt(index, data, ok = true, status = 400) { actions.splice(index, 1)[0].resolve({ok, status, json: async () => data}); },
    finishStart(data = {}) { const request = calls.at(-1); assert.equal(request.path, '/api/demo/enroll/start'); const token = request.payload.token; actions.shift().resolve({ok: true, json: async () => ({...data, token})}); return token; },
    async frame(index, ok = true) { frames[index].resolve({ok, status: ok ? 200 : 503, blob: async () => ({})}); await flush(); },
    setStatus(value) { roiStatus = value; },
    hangNextStatusRequest() { hangNextStatus = true; },
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
    const eligible = {elapsed_ms: 30000, attempts: 15, candidate_pool_count: 4,
      candidate_pool_required: 8, required: 5};
    assert.match(p.context.enrollmentStallHint(eligible), /qualified candidates so far: 4\/8. Once the pool is full, automatically select 5 to save/);
    assert.equal(p.context.enrollmentStallHint({...eligible, elapsed_ms: 29999}), '',
      'the slow-progress hint starts at 30 seconds');
    assert.equal(p.context.enrollmentStallHint({...eligible, attempts: 14}), '',
      'the hint waits for at least 15 capture attempts');
    assert.match(p.context.enrollmentStallHint({...eligible, candidate_pool_count: 5}), /qualified candidates so far: 5\/8/,
      'five candidates are not the full eight-image candidate pool');
    assert.equal(p.context.enrollmentStallHint({...eligible, candidate_pool_count: 8}), '',
      'the hint disappears when the candidate pool is full');
    assert.equal(p.context.enrollmentStallHint({...eligible, status: 'STOPPED'}), '',
      'a stopped capture must not claim that automatic collection continues');
    assert.equal(p.context.enrollmentStallHint({...eligible, status: 'CANCELLED'}), '',
      'a cancelled capture must not claim that automatic collection continues');
    assert.match(p.context.enrollmentStallHint({...eligible, status: 'NO_HAND'}), /Auto-capture will continue/,
      'a recoverable no-hand pause may explain that collection resumes automatically');
  }
  {
    const p = page(); await p.ready();
    p.setStatus({camera_ready:true,roi_status_fresh:true,quality_status:'NO_HAND',quality_reason:'tracking_lost',quality_consecutive_frames:0,quality_required_frames:5});
    await p.refreshStatus();
    assert.match(p.element('roi-status').textContent,/Palm region lost. Return your hand to resume capture automatically/);
    assert.equal(p.element('enroll').disabled,false,'one start action remains available while waiting for tracking recovery');
    p.setStatus({camera_ready:true,roi_status_fresh:false,quality_status:'NO_HAND',quality_reason:'tracking_stale',quality_consecutive_frames:0,quality_required_frames:5});
    await p.refreshStatus();
    assert.match(p.element('roi-status').textContent,/Waiting for a fresh frame and stable detection/);
  }
  for (const gate of [false, true]) {
    const storage = new Map([['palm_demo_enrollment_token', '9'.repeat(32)]]);
    const p = page(storage, gate); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:8,
      candidate_pool_required:8,kept:5,required:5,attempts:8,quality_failures:0,timeout_ms_remaining:600000});
    await flush();
    let commit;
    if (gate) await p.advance(0);
    else { commit = p.element('enroll-commit').onclick(); await flush(); }
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/commit').length, 1);
    p.finish({user_id:'p1',display_name:'P1',balance_cents:10000,recognition_ready:false});
    if (commit) await commit; else await flush();
    assert.match(p.element('notice').textContent, /Saved templates for .*recognition.*not ready/);
    assert.doesNotMatch(p.element('notice').textContent, /You can return to the access demo/);
    await p.advance(1000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/commit').length, 1,
      'a saved template with failed preparation must not be committed again automatically');
  }
  for (const next of ['identify', 'enroll']) for (const fail of [false, true]) {
    const p = page(); await p.ready();
    p.element('user').value='race'; p.element('name').value='Race'; p.element('hand').value='left';
    const old = p.element('enroll').onclick(); await flush(); p.finishStart(); await flush();
    const before = p.calls.length; await p.element('identify').onclick();
    assert.equal(p.calls.length, before, 'busy blocks concurrent actions before cancellation');
    const cancel = p.element('enroll-cancel').onclick(); await flush(); p.finishAt(1, {status:'CANCELLED'}); await cancel;
    assert.equal(p.element(next).disabled, false, 'confirmed cancellation releases the old step');
    const current = p.element(next).onclick(); await flush();
    if (fail) p.actions.splice(0,1)[0].reject(Error('old failure'));
    else p.finishAt(0, {status:'NO_HAND', reason:'old result'});
    await old; await flush();
    assert.equal(p.element('identify').disabled, true, 'old finally must not unlock the new action');
    assert.doesNotMatch(p.element('notice').textContent, /old result|old failure/);
    if (next === 'identify') p.finish({status:'UNKNOWN'});
    else { p.finishStart(); await flush(); p.finish({status:'NO_HAND',reason:'new'}); }
    await current;
  }

  {
    const p=page(new Map([['palm_demo_enrollment_token','2'.repeat(32)]])); await flush();
    p.finish({status:'PAUSED',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:1,candidate_pool_required:8,kept:0,required:5,attempts:1,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[],candidate_roi_image:'restoredcandidate'}); await flush();
    assert(p.element('enroll-thumbs').innerHTML.includes('restoredcandidate'));
    assert(p.element('enroll-thumbs').innerHTML.includes('not yet selected'));
  }
  {
    const p=page(new Map([['palm_demo_enrollment_token','2'.repeat(32)]]),true); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[]}); await flush();
    vm.runInContext('busy=true',p.context); await p.advance(0);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,0);
    vm.runInContext('busy=false',p.context); await p.advance(100);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,1,'automatic save waits for the active operation, then proceeds once');
    assert(!p.element('enroll-commit').hidden);
  }
  {
    const p=page(new Map([['palm_demo_enrollment_token','d'.repeat(32)]]),true); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[]}); await flush(); await p.advance(0);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,1,'restored gate READY commits once');
    await p.advance(10); assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,1);
    p.finish({status:'COMPLETED',display_name:'P1'}); await flush();
  }
  {
    const p=page(new Map([['palm_demo_enrollment_token','e'.repeat(32)],['palm_demo_enrollment_commit_pending','1']]),true); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[]}); await flush(); await p.advance(10);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,1,'server READY proves the previous commit did not complete, so recovery safely resumes it');
    assert(!p.element('enroll-commit').hidden);
    assert.equal(p.storage.get('palm_demo_enrollment_commit_pending'),'1','uncertainty remains recorded until the server confirms completion');
    assert.match(p.element('notice').textContent,/Verifying the previous auto-save/);
  }
  {
    const p=page(new Map([['palm_demo_enrollment_token','f'.repeat(32)]])); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[]}); await flush(); await p.advance(10);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,1,'ordinary mode automatically saves a restored READY session');
  }
  {
    const p=page(new Map([['palm_demo_enrollment_token','1'.repeat(32)]]),true); await flush();
    p.finish({status:'READY',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,selected_roi_images:[]}); await flush();
    const cancel=p.element('enroll-cancel').onclick(); p.finish({status:'CANCELLED'}); await cancel; await p.advance(0);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/commit').length,0,'cancel invalidates restored automatic commit');
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'a'.repeat(32)]]);
    const p = page(storage); await flush();
    assert.equal(p.calls[0].path, '/api/demo/enroll/status');
    p.finish({status:'PAUSED',user_id:'p1_left',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:0,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,fallback_after_ms:1000});
    await flush(); await p.advance(1250);
    const steps = p.calls.filter(x => x.path === '/api/demo/enroll/step');
    assert.equal(steps.length, 1, 'restored candidates should automatically reach selection without hand');
    assert.equal(steps[0].payload.selection_only, true);
    p.finish({status:'READY',selection_mode:'five_candidate_wait',candidate_pool_count:5,candidate_pool_required:8,kept:5,required:5,attempts:5,selected_roi_images:[]}); await flush();
    assert(p.element('notice').textContent.includes('Automatically selected from previously qualified candidates: 5'),
      'fallback completion must disclose that it selected cached qualified candidates');
  }
  {
    const p = page(new Map([['palm_demo_enrollment_token', 'b'.repeat(32)]])); await flush();
    p.finish({status:'PAUSED',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:4,candidate_pool_required:8,kept:0,required:5,attempts:4,quality_failures:0,timeout_ms_remaining:600000,fallback_after_ms:null});
    await flush(); await p.advance(9000);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,0,'four restored candidates must not trigger selection');
  }
  {
    const p = page(new Map([['palm_demo_enrollment_token', 'c'.repeat(32)]])); await flush();
    p.finish({status:'PAUSED',user_id:'p1',display_name:'P1',hand:'left',candidate_pool_count:5,candidate_pool_required:8,kept:0,required:5,attempts:5,quality_failures:0,timeout_ms_remaining:600000,fallback_after_ms:1000});
    await flush(); const cancel=p.element('enroll-cancel').onclick(); p.finish({status:'CANCELLED'}); await cancel; await p.advance(1250);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,0,'cancel invalidates restored fallback');
  }
  {
    const p = page(); await p.ready();
    const run = p.element('identify').onclick(); await flush();
    p.finish({status: 'RETRY', reason: 'GALLERY_INCOMPATIBLE_TEMPLATES'}); await run;
    assert.match(p.element('notice').textContent, /re-enroll with the original ID/i);
    assert(p.element('candidate').hidden, 'an incompatible gallery cannot show a candidate');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'slow_left'; p.element('name').value = 'Slow'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: null, candidate_pool_required: 8, timeout_seconds: 600}); await flush();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 20, quality_failures: 20,
      candidate_pool_count: 0, candidate_pool_required: 8, retry_after_ms: 2000,
      timeout_ms_remaining: 500000, reason: 'Keep the image clear'}); await flush();
    assert.match(p.element('enroll-progress').textContent, /quality retries: 20/);
    assert(!p.element('enroll-progress').textContent.includes('/null'));
    assert.match(p.element('enroll-progress').textContent, /Qualified candidates: 0\/8.*Once collection finishes, automatically select 5 photos/);
    await p.advance(1999);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1);
    await p.advance(1);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2, 'quality retries continue after backoff');
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 28, quality_failures: 20,
      candidate_pool_count: 8, candidate_pool_required: 8, selected_roi_images: []});
    await enrollment;
    assert(!p.element('enroll-commit').hidden, 'clear frames can complete the same session');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'five_left'; p.element('name').value = 'Five'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.setStatus({camera_ready:true,roi_status_fresh:true,quality_status:'NO_HAND',quality_consecutive_frames:0,quality_required_frames:5});
    p.finish({status:'NO_HAND',candidate_pool_count:5,candidate_pool_required:8,kept:0,required:5,attempts:6,fallback_after_ms:1000,reason:'Waiting for palm'});
    await enrollment; await p.advance(1249);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,1);
    await p.advance(1);
    const steps=p.calls.filter(x=>x.path==='/api/demo/enroll/step');
    assert.equal(steps.length,2); assert.equal(steps[1].payload.selection_only,true);
    p.finish({status:'READY',candidate_pool_count:5,kept:5,required:5,attempts:6,selected_roi_images:[]}); await flush();
    assert(!p.element('enroll-commit').hidden, 'five saved candidates reach confirmation without a camera capture');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value='five_camera'; p.element('name').value='Five'; p.element('hand').value='left';
    const enrollment=p.element('enroll').onclick(); await flush(); p.finishStart({candidate_pool_required:8}); await flush();
    p.finish({status:'WAIT',capture_failure:'CAMERA_UNAVAILABLE',candidate_pool_count:5,kept:0,required:5,attempts:6,fallback_after_ms:1000,reason:'Camera unavailable'}); await enrollment;
    await p.advance(1250);
    const steps=p.calls.filter(x=>x.path==='/api/demo/enroll/step');
    assert.equal(steps.length,2); assert.equal(steps[1].payload.selection_only,true);
    p.finish({status:'READY',candidate_pool_count:5,kept:5,required:5,attempts:6,selected_roi_images:[]}); await flush();
    assert(!p.element('enroll-commit').hidden, 'camera failure can finish from already-qualified candidates');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value='five_cancel'; p.element('name').value='Five'; p.element('hand').value='left';
    const enrollment=p.element('enroll').onclick(); await flush(); p.finishStart({candidate_pool_required:8}); await flush();
    p.setStatus({camera_ready:true,roi_status_fresh:true,quality_status:'NO_HAND',quality_consecutive_frames:0,quality_required_frames:5});
    p.finish({status:'NO_HAND',candidate_pool_count:5,kept:0,required:5,attempts:6,fallback_after_ms:1000,reason:'Waiting for palm'}); await enrollment;
    const cancel=p.element('enroll-cancel').onclick(); p.finish({status:'CANCELLED'}); await cancel;
    await p.advance(1500);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,1,'cancel invalidates the fallback timer');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value='five_resume'; p.element('name').value='Five'; p.element('hand').value='left';
    const enrollment=p.element('enroll').onclick(); await flush(); p.finishStart({candidate_pool_required:8}); await flush();
    p.setStatus({camera_ready:true,roi_status_fresh:true,quality_status:'NO_HAND',quality_consecutive_frames:0,quality_required_frames:5});
    p.finish({status:'NO_HAND',candidate_pool_count:5,kept:0,required:5,attempts:6,fallback_after_ms:1000,reason:'Waiting for palm'}); await enrollment; await p.refreshStatus();
    p.setStatus({camera_ready:true,roi_status_fresh:true,quality_status:'READY',quality_consecutive_frames:5,quality_required_frames:5}); await p.refreshStatus();
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,2);
    await p.advance(1500);
    assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,2,'fallback does not overlap a resumed capture');
    p.finish({status:'READY',candidate_pool_count:5,kept:5,required:5,attempts:7,selected_roi_images:[]}); await flush();
    await p.advance(500); assert.equal(p.calls.filter(x=>x.path==='/api/demo/enroll/step').length,2);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'cancel_left'; p.element('name').value = 'Cancel'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 1,
      candidate_pool_count: 0, candidate_pool_required: 8, capture_failure: 'NO_HAND', reason: 'Waiting for palm'});
    await enrollment; await p.refreshStatus();
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    const beforeDuplicateCancel = p.calls.length;
    await p.refreshStatus(); await p.element('enroll-cancel').onclick();
    assert(p.element('enroll-cancel').disabled, 'status refresh cannot enable an in-flight cancellation');
    assert.equal(p.calls.length, beforeDuplicateCancel, 'in-flight cancellation is not duplicated');
    p.actions.shift().reject(Error('Network interrupted')); await cancel;
    assert.match(p.element('notice').textContent, /Cancellation unconfirmed/);
    assert.equal(p.storage.get('palm_demo_enrollment_token'), token, 'uncertain cancellation retains the session token');
    assert(p.element('enroll-resume').disabled && p.element('enroll-commit').disabled,
      'capture and commit stay disabled while cancellation is uncertain');
    const n = p.calls.length;
    await p.element('enroll-resume').onclick(); await p.element('enroll-commit').onclick();
    await p.refreshStatus(); await p.advance(5000);
    assert.equal(p.calls.length, n, 'no capture or commit request follows an uncertain cancellation');
    assert(!p.element('enroll-cancel').disabled, 'cancellation can be retried');
    const retry = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await retry;
    assert(!p.storage.has('palm_demo_enrollment_token'), 'confirmed cancellation clears session');
    await p.frame(1); await p.refreshStatus();
    assert(!p.element('enroll').disabled, 'a new session can be started when camera and ROI are ready');
  }
  for (const status of ['COMPLETED', 'READY', 'LOST']) {
    const storage = new Map(), p = page(storage); await p.ready();
    p.element('user').value = 'commit_left'; p.element('name').value = 'Commit'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, candidate_pool_count: 8,
      candidate_pool_required: 8, selected_roi_images: []}); await enrollment;
    const commit = p.element('enroll-commit').onclick(); await flush();
    p.actions.shift().reject(Error('Response lost')); await commit;
    assert.match(p.element('notice').textContent, /Save result unconfirmed/);
    assert.equal(storage.get('palm_demo_enrollment_commit_pending'), '1');
    assert(p.element('enroll-commit').disabled && !p.element('enroll-restore').hidden);
    const count = p.calls.filter(x => x.path === '/api/demo/enroll/commit').length;
    await p.element('enroll-commit').onclick();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/commit').length, count,
      'a lost save response cannot trigger blind re-commit');
    const recover = p.element('enroll-restore').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status');
    p.finish(status === 'READY' ? {status, user_id: 'commit_left', display_name: 'Commit', hand: 'left',
      kept: 5, required: 5, attempts: 8, quality_failures: 0, candidate_pool_count: 8,
      candidate_pool_required: 8, timeout_ms_remaining: 600000, selected_roi_images: []} : {status});
    await recover;
    assert.equal(storage.has('palm_demo_enrollment_commit_pending'), status === 'READY');
    if (status === 'READY') {
      assert.equal(storage.get('palm_demo_enrollment_token'), token);
      assert(!p.element('enroll-commit').disabled, 'server-confirmed READY permits another save');
    } else {
      assert(!storage.has('palm_demo_enrollment_token'));
      if (status === 'LOST') assert.match(p.element('notice').textContent, /enrollment list/);
      else assert.match(p.element('notice').textContent, /complete/);
    }
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'restart-token'],
      ['palm_demo_enrollment_commit_pending', '1']]);
    const p = page(storage); await flush();
    assert.equal(p.calls[0].path, '/api/demo/enroll/status');
    p.finish({status: 'LOST'}); await flush();
    assert.match(p.element('notice').textContent, /enrollment list/,
      'a browser refresh preserves uncertainty after the server loses its in-memory session');
    assert(!p.element('notice').textContent.includes('not saved'));
    assert(!storage.has('palm_demo_enrollment_commit_pending'));
  }
  for (const response of ['success', 'failure']) {
    const p = page(); await p.ready();
    p.element('user').value = 'race_commit'; p.element('name').value = 'Race'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, candidate_pool_count: 8,
      candidate_pool_required: 8, selected_roi_images: []}); await enrollment;
    const commit = p.element('enroll-commit').onclick(); await flush();
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    p.finishAt(1, {status: response === 'success' ? 'COMPLETED' : 'CANCELLED'}); await cancel;
    const notice = p.element('notice').textContent;
    if (response === 'success') p.finishAt(0, {display_name: 'Race', balance_cents: 10000});
    else p.finishAt(0, {message: 'expired'}, false, 400);
    await commit;
    assert.equal(p.element('notice').textContent, notice, 'late commit response cannot replace confirmed terminal state');
    assert(!p.storage.has('palm_demo_enrollment_token') && !p.storage.has('palm_demo_enrollment_commit_pending'));
    assert(p.element('enroll-restore').hidden, 'a stale response cannot reopen recovery');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'hung_commit'; p.element('name').value = 'Hung'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, candidate_pool_count: 8,
      candidate_pool_required: 8, selected_roi_images: []}); await enrollment;
    const oldCommit = p.element('enroll-commit').onclick(); await flush();
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    p.finishAt(1, {status: 'CANCELLED'}); await cancel;
    assert(!p.element('enroll').disabled, 'confirmed terminal state releases a hung commit lock');
    p.element('user').value = 'next_left'; p.element('name').value = 'Next';
    const next = p.element('enroll').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/start');
    const nextToken = p.calls.at(-1).payload.token;
    p.finishAt(0, {message: 'old request'}, false, 400); await oldCommit;
    assert(p.element('enroll').disabled, 'the old commit must not release the new session lock');
    assert.equal(p.storage.get('palm_demo_enrollment_token'), nextToken);
    p.finishAt(0, {token: nextToken, candidate_pool_required: 8}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'Waiting for palm'}); await next;
    const finish = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await finish;
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'pending-token'],
      ['palm_demo_enrollment_commit_pending', '1']]);
    const p = page(storage); await flush();
    p.finish({status: 'READY', user_id: 'p1_left', display_name: 'P1', hand: 'left', kept: 5,
      required: 5, attempts: 8, quality_failures: 0, candidate_pool_count: 8,
      candidate_pool_required: 8, timeout_ms_remaining: 600000, selected_roi_images: []}); await flush();
    const commit = p.element('enroll-commit').onclick(); await flush();
    p.actions.shift().reject(Error('lost response')); await commit;
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
    assert.match(p.element('notice').textContent, /enrollment list/,
      'CANCELLED cannot prove a previous uncertain save was absent across a server restart');
  }
  for (const fail of [false, true]) {
    const p = page(); await p.ready();
    p.element('user').value = 'race_left'; p.element('name').value = 'Race'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.calls.at(-1).payload.token;
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    p.finishAt(1, {status: 'CANCELLED'}); await cancel;
    if (fail) p.finishAt(0, {message: 'Late error'}, false, 400);
    else p.finishAt(0, {token, max_quality_failures: 15, candidate_pool_required: 8});
    await enrollment; await flush();
    assert.match(p.element('notice').textContent, /cancel/i, 'late start cannot replace the cancellation');
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 0, 'late start cannot begin capture');
    assert(!p.storage.has('palm_demo_enrollment_token'));
  }
  for (const [gate, fail] of [[false, false], [false, true], [true, false], [true, true]]) {
    const p = page(new Map(), gate); await p.ready();
    p.element('user').value = 'p1_left'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    p.finishAt(1, {status: 'CANCELLED'}); await cancel;
    assert.match(p.element('notice').textContent, /cancel/i);
    if (fail) p.finishAt(0, {message: 'Late error'}, false, 400);
    else p.finishAt(0, {status: 'READY', kept: 5, required: 5, attempts: 8,
      timeout_ms_remaining: 60000, selected_roi_images: ['stale'], reason: 'Late result'});
    await enrollment; await p.advance(0);
    assert.match(p.element('notice').textContent, /cancel/i, 'late step cannot replace cancellation');
    assert.equal(p.element('enroll-thumbs').innerHTML, '', 'late step cannot restore stale thumbnails');
    assert(p.element('enroll-commit').hidden, 'late READY cannot expose commit');
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/commit').length, 0);
    assert.equal(p.storage.has('palm_demo_enrollment_token'), false);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'recover_left'; p.element('name').value = 'Recover'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 1, candidate_pool_count: 0,
      candidate_pool_required: 8, reason: 'Waiting for palm'}); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'});
    await enrollment;
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'a non-ready preview observed before capture is a valid loss before the next READY poll');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'cancel_left'; p.element('name').value = 'Cancel'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5}); await p.refreshStatus();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 1, candidate_pool_count: 0}); await flush();
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await enrollment;
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5}); await p.refreshStatus(); await p.advance(1000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a later READY poll must not restart an enrollment cancelled after a non-ready capture');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1_left'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1);
    await p.advance(5000);
    assert.match(p.element('notice').textContent, /still processing/);
    assert(!p.element('enroll-cancel').disabled, 'cancel stays available during a slow step');
    await p.advance(5000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1, 'slow step is never sent again');
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    assert.match(p.element('notice').textContent, /Canceling enrollment/);
    p.finishAt(0, {status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await enrollment;
    p.finishAt(0, {status: 'CANCELLED'}); await cancel;
    assert.match(p.element('notice').textContent, /cancel/i);
    await p.advance(5000);
    assert.match(p.element('notice').textContent, /cancel/i, 'a stale wait hint must not overwrite cancellation');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1_left'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'Return your hand'}); await enrollment;
    await p.advance(5000);
    assert.match(p.element('notice').textContent, /Return your hand/, 'completed step clears the wait hint');
  }
  {
    const p = page(new Map(), true); await p.frame(0); await p.refreshStatus();
    assert.match(p.element('enroll-hand-hint').textContent, /Before starting.*check.*hand/);
    assert.match(p.element('enroll-hand-hint').textContent, /automatically selects and saves five frames/);
    assert.equal(p.element('enroll').disabled, false, 'gate enrollment can start while waiting for a palm');
    p.element('user').value = 'person1'; p.element('name').value = 'Person'; p.element('hand').value = 'left';
    const pending = p.element('enroll').onclick(); await flush(); p.finishStart(); await pending;
    assert.equal(p.calls.filter(call => call.path === '/api/demo/enroll/step').length, 0, 'do not capture before the palm is ready');
    assert.match(p.element('notice').textContent, /After consecutive ready frames, the system automatically captures and selects five frames/);
    assert.match(p.element('enroll-progress').textContent, /x\/5.*not photos collected.*No candidate photos yet/);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step', 'automatically capture after readiness');
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, candidate_pool_count: 8, selected_roi_images: []});
    await flush(); await p.advance(0);
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/commit', 'gate enrollment automatically commits selected samples');
    p.finish({display_name: 'Person', enrollment_elapsed_ms: 1000}); await flush();
  }
  {
    const p = page(); await p.frame(0); await p.refreshStatus();
    assert.equal(p.element('enroll').disabled, false, 'ordinary enrollment can start while the camera is ready but no palm is present');
    assert.equal(p.element('identify').disabled, true, 'identification still waits for a ready palm');
    p.element('user').value = 'wait_for_hand'; p.element('name').value = 'Wait'; p.element('hand').value = 'left';
    const start = p.element('enroll').onclick(); await flush(); p.finishStart(); await start;
    assert.equal(p.calls.filter(call => call.path === '/api/demo/enroll/step').length, 0, 'no capture request is sent while the ROI is not ready');
    assert.match(p.element('notice').textContent, /Enrollment started. After consecutive ready frames, the system automatically captures and selects five frames/);
    assert.match(p.element('enroll-progress').textContent, /not photos collected/);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus(); await flush();
    assert.equal(p.calls.filter(call => call.path === '/api/demo/enroll/step').length, 1, 'ordinary enrollment resumes automatically when the ROI becomes ready');
    await p.refreshStatus(); await flush();
    assert.equal(p.calls.filter(call => call.path === '/api/demo/enroll/step').length, 1, 'repeated READY status cannot start a concurrent capture');
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, candidate_pool_count: 8, selected_roi_images: []});
    await flush(); await flush();
    await p.advance(0);
    assert.equal(p.calls.filter(call => call.path === '/api/demo/enroll/commit').length, 1, 'ordinary mode automatically saves after selecting five photos');
    assert.match(p.element('notice').textContent,/Saving/);
    p.finish({display_name: 'Wait', enrollment_elapsed_ms: 1200}); await flush();
  }
  {
    const p = page(); await p.ready();
    assert.equal(p.element('preview').style.aspectRatio, '640 / 360', 'preview must match the actual 16:9 camera frame');
    p.setImageSize(800, 600); await p.advance(200); await p.frame(1);
    assert.equal(p.element('preview').style.aspectRatio, '800 / 600', 'preview ratio must follow a changed camera mode');
    const run = p.element('identify').onclick(); await flush();
    await p.advance(47);
    p.finish({status: 'UNKNOWN', reason: 'NO_MATCH', timing_ms: {
      capture_and_extract: 213.4, gallery: 18.2, total: 231.6
    }});
    await run;
    const timing = p.element('recognition-timing').textContent;
    assert(timing.includes('Browser round trip 47 ms'));
    assert(timing.includes('Server capture+Features 213.4 ms'));
    assert(timing.includes('Gallery verification+Matching 18.2 ms'));
    assert(timing.includes('Server total 231.6 ms'),
      'timings must be visible for rejected queries as well as matches');
  }
  {
    const p = page(); await p.ready();
    p.hangNextStatusRequest();
    void p.context.pollStatus(); await flush();
    const hung = p.statusRequests.at(-1);
    assert(!p.element('identify').disabled, 'the previous READY state may remain only during the bounded request deadline');
    await p.advance(2500);
    assert(hung.options.signal.aborted, 'a hanging read-only status request must be aborted at its deadline');
    assert(p.element('identify').disabled && p.element('enroll').disabled,
      'status timeout invalidates stale READY and disables capture actions');
    assert(p.element('roi-status').textContent.includes('status unavailable'));
    await p.advance(500);
    assert(!p.element('identify').disabled, 'a fresh READY response restores capture actions');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5});
    hung.resolve(); await flush();
    assert(!p.element('identify').disabled && p.element('roi-status').textContent.includes('Consecutive ready frames 5/5'),
      'a late response from the timed-out poll cannot overwrite a newer READY response');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1_left'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', resume_required: true, reason: 'No palm detected'});
    await enrollment;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'a READY status alone does not count as recovery after a high-resolution NO_HAND result');
    await p.advance(750); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'the existing bounded preview/capture mismatch retry still runs once');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', resume_required: true, reason: 'Still no palm detected'});
    await flush();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    p.hangNextStatusRequest(); void p.context.pollStatus(); await flush();
    await p.advance(2500);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a status timeout cannot fake a non-READY transition and bypass the one-retry limit');
    await p.advance(500); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a READY response after timeout alone cannot auto-resume a paused enrollment');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'a real non-READY then READY transition restores automatic resume');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1_left'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', resume_required: true,
      timeout_ms_remaining: 500, timeout_seconds_remaining: 1, reason: 'No palm detected'});
    await enrollment;
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    await p.advance(500);
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status',
      'the local enrollment deadline is checked with the server');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'a fresh READY status cannot auto-resume after the local enrollment deadline');
    p.finish({status: 'EXPIRED'}); await flush();
  }
  {
    const p = page();
    await p.frame(0);
    await p.advance(199);
    assert.equal(p.frames.length, 1, 'the preview poller should wait for its configured refresh interval');
    await p.advance(1);
    assert.equal(p.frames.length, 2, 'the next preview request should start after the configured 200 ms');
  }
  {
    const p = page();
    await p.advance(1000);
    assert.equal(p.frames.length, 1, 'a slow in-flight request must not overlap another preview poll');
    await p.frame(0);
    await p.advance(199);
    assert.equal(p.frames.length, 1, 'the refresh delay starts after the previous image finishes loading');
    await p.advance(1);
    assert.equal(p.frames.length, 2);
  }
  {
    const p = page();
    await p.frame(0, false);
    await p.advance(299);
    assert.equal(p.frames.length, 1, 'camera errors retain a slower retry cadence');
    await p.advance(1);
    assert.equal(p.frames.length, 2, 'camera retries resume after 300 ms');
  }
  {
    const p = page();
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    await p.element('identify').onclick(); assert.equal(p.calls.length, 0);
    p.setImageLoading(false); await p.frame(0);
    assert(p.element('identify').disabled, 'a received image must be displayed before enabling capture');
    p.element('live').onload(); await flush();
    assert(!p.element('live').hidden && p.element('identify').disabled && !p.element('enroll').disabled,
      'a fresh no-hand status may start enrollment but must keep identification disabled');
    assert(p.element('roi-status').textContent.includes('Waiting for palm'), 'ordinary mode should show a clear no-hand instruction');
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
    assert(p.element('roi-status').textContent.includes('status unavailable'));
    p.failStatus(false); await p.refreshStatus();
    assert(!p.element('identify').disabled);
    assert(p.element('camera-status').textContent.includes('Camera connected'));
    await p.advance(300); await p.context.preview();
    assert.equal(p.frames.length, 2, 'an active preview request must not overlap another poll');
    await p.frame(1, false);
    assert(p.element('live').hidden && !p.element('live').src);
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    assert(p.element('camera-status').textContent.includes('unavailable'));
    assert(p.revoked.includes('blob:preview-1'));
    p.setImageLoading(true); await p.advance(300); await p.frame(2);
    await p.refreshStatus();
    assert(!p.element('live').hidden && !p.element('identify').disabled);
  }
  {
    const p = page(new Map([['palm_demo_enrollment_token', 'restore-pending']]));
    await p.frame(0);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert(p.element('identify').disabled && p.element('enroll').disabled,
      'a READY camera must not enable new actions while the saved enrollment token is being checked');
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/status').length, 1);
    p.finish({status: 'PAUSED', user_id: 'p1', display_name: 'P1', hand: 'left', kept: 2,
      required: 5, attempts: 4, quality_failures: 0, duplicate_frames: 0,
      candidate_pool_count: 4, candidate_pool_required: 8, max_quality_failures: 15,
      selected_roi_images: [], elapsed_ms: 1500, timeout_seconds_remaining: 118});
    await flush();
    assert(p.element('identify').disabled && p.element('enroll').disabled,
      'restoring a live enrollment keeps identification and new enrollment locked');
    assert(!p.element('enroll-cancel').hidden && !p.element('enroll-cancel').disabled,
      'the restored session can be cancelled after its status is confirmed');
    assert(p.element('enroll-progress').textContent.includes('Enrollment time: 1.5 s'));
    assert(p.element('enroll-progress').textContent.includes('Idle time remaining: 118 s'));
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'the first READY poll resumes exactly one step loop for the restored token');
  }
  {
    const p = page(); await p.ready();
    p.setStatus({camera_ready: true, roi_status_fresh: true,
      quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5,
      demo_quality_status: 'LOW_QUALITY', demo_quality_reason: 'sharpness_below_minimum',
      demo_quality_consecutive_frames: 0, demo_quality_required_frames: 5,
      demo_quality: {sharpness: 1.5, contrast: 14},
      demo_quality_config: {min_sharpness: 2, min_contrast: 12}});
    await p.refreshStatus();
    assert(p.element('identify').disabled && !p.element('enroll').disabled,
      'low-quality status may start enrollment waiting, but must not enable identification');
    assert(p.element('roi-status').textContent.includes('blurry'));
    assert(p.element('roi-status').textContent.includes('Insufficient image quality'));
    assert(p.element('roi-status').textContent.includes('Consecutive ready frames 0/5'));
    assert(p.element('roi-status').textContent.includes('sharpness 1.50 / 2.00'));
    assert(p.element('roi-status').textContent.includes('contrast 14.00 / 12.00'));
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
    assert(p.element('identify').disabled && p.element('camera-status').textContent.includes('stopped updating'));
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
    await p.advance(1000); assert(p.element('notice').textContent.includes(' s'));
    await p.frame(1, false); p.finish({status: 'UNKNOWN'}); await run;
    assert.equal(p.intervalCount(), 0);
    assert(p.element('identify').disabled, 'finishing an action must not re-enable capture after camera loss');
    await p.advance(300); await p.frame(2); await p.refreshStatus();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    run = p.element('enroll').onclick(); await flush(); await p.element('enroll').onclick();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/start').length, 1);
    p.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    for (let kept = 1; kept <= 8; kept++) {
      assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
      p.finish({status: kept === 8? 'READY' : 'COLLECTING', kept: kept === 8? 5 : 0,
        candidate_pool_count: kept, candidate_pool_required: 8, required: 5, attempts: kept,
        elapsed_ms: kept === 8? 4321 : 1200, timeout_seconds_remaining: 116,
        selected_roi_images: kept === 8? ['one','two','three','four','five'] : undefined,
        candidate_roi_image: kept < 8? `candidate${kept}` : undefined}); await flush();
      if (kept < 8) {
        assert(p.element('enroll-thumbs').innerHTML.includes(`candidate${kept}`));
        assert(p.element('enroll-thumbs').innerHTML.includes('not yet selected'));
      }
    }
    await run;
    assert(p.element('enroll-thumbs').innerHTML.includes('one'));
    assert(!p.element('enroll-thumbs').innerHTML.includes('candidate7'));
    assert(p.element('enroll-progress').textContent.includes('5/5'));
    assert(p.element('enroll-progress').textContent.includes('Idle time remaining: 116 s'));
    assert(p.element('notice').textContent.includes('Auto-capture time: 4.3 s'));
    await p.advance(0);
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/commit');
    assert.equal(p.calls.at(-1).payload.confirm_hand, 'left');
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    assert(!p.element('enroll-cancel').disabled);
    p.finish({display_name: 'P1', balance_cents: 10000, enrollment_elapsed_ms: 9876}); await flush();
    assert(p.element('notice').textContent.includes('Total enrollment time: 9.9 s'));
    assert(!p.element('user').disabled && !p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    p.finish({status: 'KEPT', kept: 1, required: 5, attempts: 1, duplicate_frames: 0, quality_failures: 0}); await flush();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 17, duplicate_frames: 16,
              quality_failures: 4, candidate_pool_count: 2, candidate_pool_required: 8, elapsed_ms: 35000,
              retry_after_ms: 700, reason: 'Move your hand'}); await flush();
    assert(p.element('enroll-progress').textContent.includes('duplicates skipped: 16'));
    assert(p.element('notice').textContent.includes('Move your hand'));
    assert(p.element('notice').textContent.includes('Elapsed: 35 s; qualified candidates so far: 2/8. Once the pool is full, automatically select 5 to save'));
    assert(p.element('notice').textContent.includes('Once the pool is full, automatically select 5 to save'));
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    const cancel = p.element('enroll-cancel').onclick();
    assert(p.element('notice').textContent.includes('Canceling enrollment'));
    p.finish({status: 'CANCELLED'}); await cancel;
    await p.advance(700); await run;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    assert(!p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const start = p.element('enroll').onclick(); await flush();
    const recoverToken = p.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
    p.actions.shift().reject(Error('temporary connection loss')); await start;
    assert(!p.element('enroll-resume').hidden && !p.element('enroll-resume').disabled,
      'a failed step must leave the same enrollment resumable');
    const retry = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.at(-1).payload.token, recoverToken);
    p.actions.shift().reject(Error('temporary connection loss')); await retry;
    assert(!p.element('enroll-resume').hidden && !p.element('enroll-resume').disabled,
      'a failed resume must remain retryable');
    const recovered = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.at(-1).payload.token, recoverToken);
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 20, quality_failures: 4,
      duplicate_frames: 7, candidate_pool_count: 2, candidate_pool_required: 8, elapsed_ms: 35000,
      capture_failure: 'NO_HAND', reason: 'Continuous capture paused'}); await recovered;
    assert(!p.element('enroll-resume').hidden);
    assert(p.element('notice').textContent.includes('Elapsed: 35 s; qualified candidates so far: 2/8. Once the pool is full, automatically select 5 to save'),
      'tracking loss after slow progress includes actionable candidate progress');
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(p.element('enroll-resume').hidden);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    const cameraToken = p.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    p.finish({status: 'WAIT', kept: 1, required: 5, attempts: 3, duplicate_frames: 1,
      quality_failures: 0, candidate_pool_count: 2, candidate_pool_required: 8,
      capture_failure: 'CAMERA_UNAVAILABLE', retry_after_ms: 500,
      reason: 'Camera frame temporarily unavailable. Check the connection and retry.'}); await run;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'camera loss pauses automatic steps instead of retrying every 500 ms');
    assert(p.element('enroll-resume').hidden === false);
    assert(p.element('enroll-progress').textContent.includes('Qualified candidates: 2/8'),
      'candidate-pool progress is retained while paused');
    assert(p.element('notice').textContent.includes('Enrollment paused'));
    await p.advance(2000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'no repeated capture request is made while camera recovery is pending');
    p.setStatus({camera_ready: false, roi_status_fresh: false, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'fresh camera/ROI readiness resumes the same session once');
    assert.equal(p.calls.at(-1).payload.token, cameraToken);
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'repeated READY polls do not launch parallel enrollment loops');
    p.finish({status: 'NO_HAND', kept: 1, required: 5, attempts: 4, candidate_pool_count: 2,
      candidate_pool_required: 8, capture_failure: 'NO_HAND', resume_required: true,
      reason: 'Continuous capture paused'}); await flush();
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'camera_left'; p.element('name').value = 'Camera'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 1,
      candidate_pool_count: 1, candidate_pool_required: 8,
      capture_failure: 'CAMERA_UNAVAILABLE', reason: 'Camera frame temporarily unavailable'}); await enrollment;
    await p.advance(4999);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'camera recovery must not retry before the five-second delay');
    await p.frame(1); await p.refreshStatus(); await p.advance(1);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'fresh ready preview and ROI automatically recover a camera mismatch');
    assert.equal(p.calls.at(-1).payload.token, token);
    await p.advance(1000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'the recovery loop cannot overlap a pending capture');
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 2,
      candidate_pool_count: 1, candidate_pool_required: 8,
      capture_failure: 'CAMERA_UNAVAILABLE', reason: 'Camera frame temporarily unavailable'}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
    await p.advance(10000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'cancellation invalidates the pending camera retry');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'offline_left'; p.element('name').value = 'Offline'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'WAIT', kept: 0, required: 5, attempts: 1,
      candidate_pool_count: 0, candidate_pool_required: 8,
      capture_failure: 'CAMERA_UNAVAILABLE', reason: 'Camera unavailable'}); await enrollment;
    p.setStatus({camera_ready: false, roi_status_fresh: false, quality_status: 'NO_HAND',
      quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus(); await p.advance(11000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'while camera and ROI stay unavailable no capture request may be sent');
    vm.runInContext('cameraReady=true', p.context);
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY',
      quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a genuine recovery transition resumes once without waiting for a polling timer');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const run = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15}); await flush();
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'NO_HAND', quality_consecutive_frames: 0, quality_required_frames: 5});
    await p.refreshStatus();
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 1, duplicate_frames: 0,
      quality_failures: 0, capture_failure: 'NO_HAND', resume_required: true,
      reason: 'No palm detected. Auto-capture paused. Place your hand in view. When your palm is ready, click “Continue capture”, or cancel.'}); await flush();
    assert(p.element('notice').textContent.includes('paused'));
    assert(p.element('enroll-progress').textContent.includes('quality retries: 0'));
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
      capture_failure: 'NO_HAND', resume_required: true, reason: 'Continuous capture paused'}); await flush();
    await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a NO_HAND high-resolution capture while preview remains READY does not auto-loop');
    assert(!p.element('enroll-resume').disabled,
      'manual resume stays available after the preview reports READY again');
    await p.advance(750);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'one delayed retry recovers a transient preview/high-resolution mismatch');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 3, quality_failures: 0,
      capture_failure: 'NO_HAND', resume_required: true, reason: 'Continuous capture paused'}); await flush();
    await p.advance(1000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'a second mismatch pauses without creating an automatic retry loop');
    const resume = p.element('enroll-resume').onclick(); await flush();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 4,
      'manual resume remains available after the bounded retry is exhausted');
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 4, quality_failures: 0,
      capture_failure: 'NO_HAND', resume_required: true, reason: 'Continuous capture paused'}); await flush();
    await resume;
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel; await run;
    assert(p.element('enroll-resume').hidden, 'cancel clears the paused resume control');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'quality_left'; p.element('name').value = 'Quality'; p.element('hand').value = 'left';
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/step');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'LOW_QUALITY', quality_reason: 'sharpness_below_minimum', quality_consecutive_frames: 0, quality_required_frames: 5});
    p.finish({status: 'WAIT', candidate_pool_count: 0, candidate_pool_required: 8, kept: 0, required: 5,
      attempts: 1, quality_failures: 1, retry_after_ms: 500, capture_failure: 'ROI_NOT_READY', reason: 'Palm image quality not ready'}); await enrollment;
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'ROI_NOT_READY breaks the continuous step loop');
    assert(!p.element('enroll-resume').hidden && p.element('enroll-resume').disabled,
      'ROI_NOT_READY pauses capture until the quality gate is READY');
    assert(p.element('notice').textContent.includes('capture resumes after consecutive quality-ready frames'));
    await p.refreshStatus();
    await p.advance(1500);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 1,
      'polling LOW_QUALITY never sends another capture step');
    p.setStatus({camera_ready: true, roi_status_fresh: true, quality_status: 'READY', quality_consecutive_frames: 5, quality_required_frames: 5});
    await p.refreshStatus();
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'five-frame READY automatically resumes the same session');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'auto_left'; p.element('name').value = 'Auto'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({candidate_pool_required: 8}); await flush();
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await enrollment;
    await p.refreshStatus(); await p.advance(750);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2);
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await flush();
    await p.refreshStatus(); await p.advance(4999);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 2,
      'a repeated preview/capture mismatch waits five seconds before retrying');
    vm.runInContext('cameraReady=true', p.context); await p.refreshStatus(); await p.advance(1);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'a stable ready preview retries automatically after the longer backoff');
    await p.advance(5000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'a pending capture cannot overlap another retry');
    p.finish({status: 'NO_HAND', capture_failure: 'NO_HAND', reason: 'No palm detected'}); await flush();
    const cancel = p.element('enroll-cancel').onclick(); p.finish({status: 'CANCELLED'}); await cancel;
    await p.advance(6000);
    assert.equal(p.calls.filter(x => x.path === '/api/demo/enroll/step').length, 3,
      'cancel invalidates the scheduled retry');
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    p.finish({status: 'NO_HAND', kept: 0, required: 5, attempts: 1, quality_failures: 0,
      duplicate_frames: 0, candidate_pool_count: 0, candidate_pool_required: 8,
      capture_failure: 'NO_HAND', resume_required: true, timeout_ms_remaining: 1500,
      timeout_seconds_remaining: 2, reason: 'No palm detected'}); await enrollment;
    assert(p.element('enroll-resume').disabled, 'paused capture remains disabled until the camera is ready');
    assert(p.element('enroll-progress').textContent.includes('Idle time remaining: 2 s'));
    await p.advance(1000);
    assert(p.element('enroll-progress').textContent.includes('Idle time remaining: 1 s'),
      'the countdown must keep advancing while NO_HAND has paused capture');
    await p.advance(500);
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status',
      'zero on the client clock must query the server instead of clearing the token locally');
    assert(p.element('enroll-cancel').disabled === false, 'cancel remains available during expiry verification');
    p.actions.shift().reject(Error('temporary status failure')); await flush();
    assert(p.storage.has('palm_demo_enrollment_token'), 'an uncertain status response must preserve the session token');
    assert(!p.element('enroll-restore').hidden && p.element('enroll-commit').disabled,
      'failed expiry verification exposes status retry but keeps save disabled');
    const restore = p.element('enroll-restore').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status');
    p.finish({status: 'EXPIRED'}); await restore;
    assert(!p.storage.has('palm_demo_enrollment_token'));
    assert(p.element('enroll-progress').textContent.includes('Unsaved candidates cleared'));
    assert(p.element('enroll-resume').hidden && p.element('enroll-cancel').hidden);
  }
  {
    const p = page(); await p.ready();
    p.element('user').value = 'p1'; p.element('name').value = 'P1'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    p.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    p.finish({status: 'READY', kept: 5, required: 5, attempts: 8, quality_failures: 0,
      duplicate_frames: 0, candidate_pool_count: 8, candidate_pool_required: 8,
      step_elapsed_ms: 47.5,
      timeout_ms_remaining: 1500, timeout_seconds_remaining: 2,
      selected_roi_images: ['a','b','c','d','e']}); await enrollment;
    assert(p.element('enroll-progress').textContent.includes('Server processing 48 ms'));
    assert(p.element('enroll-progress').textContent.includes('Frame round trip 0 ms'));
    assert(!p.element('enroll-commit').disabled, 'the active READY session may be confirmed before the deadline');
    await p.advance(0);
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/commit',
      'a selected set is automatically committed before the enrollment deadline');
    assert(p.element('enroll-commit').disabled,
      'the commit control is disabled while automatic saving is in flight');
    p.finish({display_name: 'P1', enrollment_elapsed_ms: 1200}); await flush();
    assert(p.element('enroll-commit').hidden && p.element('enroll-thumbs').innerHTML !== '',
      'successful automatic saving clears the active session while keeping the selected preview');
    assert(p.element('notice').textContent.includes('Enrolled P1'));
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); await p.element('confirm').onclick(); await p.element('retry').onclick();
    assert.equal(p.calls.length, 2); p.actions.shift().reject(Error('lost confirmation response')); await run;
    assert(p.element('notice').textContent.includes('status needs verification'));
    assert(!p.element('notice').textContent.includes('no charge'));
    assert(p.element('identify').disabled && p.element('enroll').disabled);
    await p.element('identify').onclick(); await p.element('enroll').onclick();
    assert.equal(p.calls.length, 2, 'uncertain confirmation must preserve its token and block new capture actions');
    assert(!p.element('confirm').disabled && !p.element('retry').disabled);
    run = p.element('retry').onclick();
    p.finish({status: 'PAID', payment_status: 'SUCCESS', display_name: 'P1', balance_cents: 8000, amount_cents: 2000}); await run;
    assert(p.element('candidate').hidden);
    assert(p.element('notice').textContent.includes('Simulated payment successful') && p.element('notice').textContent.includes('80.00'));
    assert(!p.element('notice').textContent.includes('no charge')); assert(!p.element('identify').disabled);
  }
  {
    const p = page(); await p.ready(); await identify(p, 'retry-confirm');
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('confirm').onclick(); assert.equal(p.calls.at(-1).payload.token, 'retry-confirm');
    p.finish({status: 'SUCCESS', display_name: 'P1', amount_cents: 2000, balance_cents: 8000}); await run;
    assert(p.element('notice').textContent.includes('Simulated payment successful'));
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('retry').onclick();
    p.finish({status: 'PAID', payment_status: 'INSUFFICIENT_BALANCE', display_name: 'P1', balance_cents: 1000}); await run;
    assert(p.element('notice').textContent.includes('Insufficient simulated balance') && p.element('notice').textContent.includes('no charge'));
    assert(!p.element('notice').textContent.includes('payment successful'));
  }
  {
    const p = page(); await p.ready(); await identify(p);
    let run = p.element('confirm').onclick(); p.actions.shift().reject(Error('network')); await run;
    run = p.element('retry').onclick(); p.finish({status: 'UNCONFIRMED'}); await run;
    assert(p.element('identify').disabled && !p.element('candidate').hidden);
    assert(!p.element('notice').textContent.includes('no charge'));
    run = p.element('retry').onclick(); p.finish({status: 'CANCELLED'}); await run;
    assert(p.element('candidate').hidden && !p.element('identify').disabled);
    assert(p.element('notice').textContent.includes('no charge'));
  }
  {
    const storage = new Map(), first = page(storage); await first.ready();
    first.element('user').value = 'p1_left'; first.element('name').value = 'P1'; first.element('hand').value = 'left';
    const enrollment = first.element('enroll').onclick(); await flush();
    const refreshToken = first.finishStart({max_quality_failures: 15, candidate_pool_required: 8}); await flush();
    first.finish({status: 'READY', kept: 5, required: 5, attempts: 8, quality_failures: 0,
      candidate_pool_count: 8, candidate_pool_required: 8, selected_roi_images: ['a','b','c','d','e']});
    await enrollment;
    assert.equal(storage.get('palm_demo_enrollment_token'), refreshToken);

    const refreshed = page(storage); await flush();
    assert.equal(refreshed.calls[0].path, '/api/demo/enroll/status');
    assert.equal(refreshed.calls[0].payload.token, refreshToken);
    refreshed.finish({status: 'READY', user_id: 'p1_left', display_name: 'P1', hand: 'left', kept: 5,
      required: 5, attempts: 8, quality_failures: 0, duplicate_frames: 0, candidate_pool_count: 8,
      candidate_pool_required: 8, max_quality_failures: 15, timeout_ms_remaining: 2000,
      timeout_seconds_remaining: 2, selected_roi_images: ['a','b','c','d','e']});
    await flush();
    assert.equal(refreshed.element('user').value, 'p1_left');
    assert.equal(refreshed.element('hand').value, 'left');
    assert(!refreshed.element('enroll-commit').hidden, 'a READY session restores its automatic save action');
    assert(refreshed.element('enroll-thumbs').innerHTML.includes('data:image/png;base64,e'));
    await refreshed.advance(0);
    assert.equal(refreshed.calls.filter(call => call.path === '/api/demo/enroll/commit').length, 1,
      'a restored READY session automatically commits the selected five photos');
    refreshed.finish({display_name: 'P1', balance_cents: 10000, enrollment_elapsed_ms: 9876}); await flush();
    assert(!storage.has('palm_demo_enrollment_token'), 'confirmed automatic save clears the refresh token');
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
      capture_failure: 'NO_HAND', resume_required: true, reason: 'Continuous capture paused'}); await flush();
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token'));
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'expired-token']]), p = page(storage); await flush();
    p.finish({status: 'EXPIRED'}); await flush();
    assert(!storage.has('palm_demo_enrollment_token'));
    assert(p.element('notice').textContent.includes('timed out'));
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'lost-after-restart-token']]), p = page(storage); await flush();
    p.finish({status: 'LOST'}); await flush();
    assert(!storage.has('palm_demo_enrollment_token'), 'a process-lost session must clear stale recovery data');
    assert(p.element('notice').textContent.includes('candidates were not saved'));
    assert(p.element('enroll-restore').hidden, 'a process-lost session must not remain stuck on restore');
    assert(p.element('enroll-cancel').hidden, 'clearing the token returns to the normal start state');
  }
  {
    const storage = new Map([['palm_demo_enrollment_token', 'temporary-network-token']]), p = page(storage); await flush();
    p.actions.shift().reject(Error('temporary network loss')); await flush();
    assert.equal(storage.get('palm_demo_enrollment_token'), 'temporary-network-token',
      'a temporary status query failure must preserve the only session token');
    assert(!p.element('enroll-restore').hidden, 'the page exposes an explicit status retry');
    assert(!p.element('enroll-cancel').hidden, 'the still-unknown server session can be cancelled');
    assert(p.element('enroll-resume').hidden, 'capture cannot resume until session state is confirmed');
    assert(p.element('notice').textContent.includes('token retained'));
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
    const storage = new Map(), p = page(storage); await p.ready();
    p.element('user').value = 'p5_left'; p.element('name').value = 'P5'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const firstStart = p.calls.at(-1);
    assert.equal(firstStart.path, '/api/demo/enroll/start');
    const token = firstStart.payload.token;
    assert.match(token, /^[0-9a-f]{32}$/);
    assert.equal(storage.get('palm_demo_enrollment_token'), token,
      'client stores the recovery token before sending start');
    assert.equal(JSON.parse(storage.get('palm_demo_enrollment_start')).token, token);
    p.actions.shift().reject(Error('response lost after server created session'));
    await enrollment;
    assert(!p.element('enroll-cancel').hidden, 'known client token keeps cancel available after a lost response');
    assert(!p.element('enroll-restore').hidden, 'the same start request can be replayed to recover its result');
    assert.equal(p.element('enroll-restore').textContent, 'Retry start / Recover');

    const replay = p.element('enroll-restore').onclick(); await flush();
    const replayStart = p.calls.at(-1);
    assert.equal(replayStart.path, '/api/demo/enroll/start');
    assert.equal(replayStart.payload.token, token, 'retry reuses the idempotent client token');
    p.finish({token, kept: 0, required: 5, candidate_pool_required: 8, max_quality_failures: 15,
      timeout_seconds: 120, timeout_ms_remaining: 120000}); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/status', 'successful replay confirms the same session');
    p.finish({status: 'PAUSED', user_id: 'p5_left', display_name: 'P5', hand: 'left', kept: 0, required: 5,
      attempts: 0, quality_failures: 0, duplicate_frames: 0, candidate_pool_count: 0,
      candidate_pool_required: 8, max_quality_failures: 15, timeout_ms_remaining: 119000,
      timeout_seconds_remaining: 119, selected_roi_images: []});
    await replay;
    assert.equal(storage.get('palm_demo_enrollment_token'), token);
    assert(p.element('enroll-restore').hidden);
    assert(!p.element('enroll-cancel').hidden);
    assert(!p.element('enroll-resume').hidden);
    const cancel = p.element('enroll-cancel').onclick();
    p.finish({status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token') && !storage.has('palm_demo_enrollment_start'));
  }
  {
    const storage = new Map(), p = page(storage); await p.ready();
    p.element('user').value = 'p6_left'; p.element('name').value = 'P6'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.calls.at(-1).payload.token;
    p.actions.shift().reject(Error('start response lost')); await enrollment;

    const replay = p.element('enroll-restore').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/start');
    assert.equal(p.calls.at(-1).payload.token, token);
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/cancel');
    p.finishAt(1, {status: 'CANCELLED'}); await cancel;
    assert(!storage.has('palm_demo_enrollment_token'));
    p.finishAt(0, {message: 'This enrollment request has ended. Start again.'}, false, 400); await replay;
    assert(!storage.has('palm_demo_enrollment_token') && !storage.has('palm_demo_enrollment_start'),
      'a late replay rejection after cancellation must not restore stale client state');
    assert(p.element('enroll-cancel').hidden);
  }
  {
    const storage = new Map(), p = page(storage); await p.ready();
    p.element('user').value = 'p7_left'; p.element('name').value = 'P7'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    const token = p.calls.at(-1).payload.token;
    assert.equal(storage.get('palm_demo_enrollment_token'), token);
    const cancel = p.element('enroll-cancel').onclick(); await flush();
    assert.equal(p.calls.at(-1).path, '/api/demo/enroll/cancel');
    p.finishAt(1, {status: 'CANCELLED'}); await cancel;
    p.finishAt(0, {message: 'This enrollment request has ended. Start again.'}, false, 400); await enrollment;
    assert(!storage.has('palm_demo_enrollment_token') && !storage.has('palm_demo_enrollment_start'),
      'cancel arriving before the original start response must prevent a stranded client session');
    assert(p.element('enroll-cancel').hidden);
  }
  {
    const storage = new Map(); storage.failSet = true;
    const p = page(storage); await p.ready();
    p.element('user').value = 'p3_left'; p.element('name').value = 'P3'; p.element('hand').value = 'left';
    const enrollment = p.element('enroll').onclick(); await flush();
    await enrollment;
    assert(!p.calls.some(call => call.path === '/api/demo/enroll/start'),
      'storage failure is detected before creating a server session');
    assert(p.element('notice').textContent.includes('enrollment has not started'));
    assert(p.element('enroll-cancel').hidden && p.element('enroll-resume').hidden);
  }
})().then(() => { clearTimeout(watchdog); console.log('UI interaction checks passed.'); })
  .catch(error => { clearTimeout(watchdog); console.error(error); process.exitCode = 1; });
