"""Dedicated local page for labeled, full-resolution palm image collection."""

HTML = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>掌纹高清采集</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f5f7;color:#17212b;font:16px system-ui,sans-serif}
header,main{max-width:1140px;margin:auto;padding:18px}header{display:flex;justify-content:space-between;align-items:center;gap:12px}
h1{font-size:1.5rem;margin:0}h2{font-size:1.1rem;margin:0 0 12px}a{color:#125e9c}
main{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(290px,1fr);gap:16px;padding-top:0}
.card{background:white;border:1px solid #dce2e8;border-radius:12px;padding:16px;box-shadow:0 2px 8px #0001}
.preview{background:#111;border-radius:8px;overflow:hidden;aspect-ratio:4/3;display:flex;align-items:center}
.preview img{width:100%;height:100%;object-fit:contain}.hint{color:#526270;font-size:.9rem;line-height:1.45}
label{display:block;font-weight:600;margin:12px 0 5px}input,select,textarea,button{font:inherit}
input,select,textarea{width:100%;padding:10px;border:1px solid #b9c4cc;border-radius:7px;background:white}
textarea{min-height:62px;resize:vertical}button{border:0;border-radius:8px;padding:11px 15px;background:#125e9c;color:white;cursor:pointer;margin-top:14px}
button:disabled{opacity:.55;cursor:wait}.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.secondary{background:#687781;margin-left:8px}
#state{white-space:pre-wrap;border-radius:8px;padding:11px;background:#eaf1f7;margin-top:14px;min-height:44px}
.readiness{padding:12px;border-radius:8px;background:#eef3f7;margin-top:12px;font-weight:700}.readiness.ready{background:#dcf5e5;color:#176332}.readiness.wait{background:#fff1dd;color:#805000}
#progress{font-weight:700;margin-top:10px}.download{display:inline-block;margin-top:14px;padding:10px 14px;border-radius:8px;background:#176332;color:white;text-decoration:none}
#delete-current{background:#a52828}.danger{background:#a52828!important}.danger:hover{background:#861f1f!important}.session-list{display:grid;gap:8px}.session-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:11px 12px;border:1px solid #dce2e8;border-radius:8px;background:#f8fafb}.session-info{min-width:0}.session-title{font-weight:700}.session-meta{color:#526270;font-size:.88rem;line-height:1.4;overflow-wrap:anywhere}.session-row button{flex:0 0 auto;margin:0;padding:8px 11px}.empty-sessions{color:#526270}
#samples{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}#samples button{margin:0;background:#526b80;padding:7px 10px}
#shot{display:block;width:auto;max-width:100%;max-height:430px;height:auto;border-radius:8px;cursor:crosshair;background:#111}#shot[hidden]{display:none}
#crop{width:100%;max-width:512px;height:auto;aspect-ratio:1;background:#e6ebef;image-rendering:pixelated;border-radius:8px}
.diagnostics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:16px 0}.diagnostics[hidden]{display:none}.diagnostics figure{margin:0}.diagnostics img{display:block;width:100%;max-width:512px;aspect-ratio:1;object-fit:contain;background:#e6ebef;border-radius:8px}.diagnostics figcaption{margin-top:5px;color:#526270;font-size:.9rem}
.wide{grid-column:1/-1}.links{display:flex;gap:18px;flex-wrap:wrap;margin:8px 0}
@media(max-width:800px){main{grid-template-columns:1fr}.wide{grid-column:1}}@media(max-width:520px){.diagnostics{grid-template-columns:1fr}}
</style></head><body>
<header><h1>掌纹高清采集 · 每组 10 张</h1><span><a href="/palmir">PalmIR 恢复对比</a> · <a href="/">返回采集页</a></span></header>
<main><section class="card"><h2>实时预览 · 480×360</h2><div class="preview"><img id="live" src="/frame.jpg" alt="实时画面"></div>
<div id="readiness" class="readiness">开始采集后即可拍摄，无需等待稳定提示。</div><div id="progress">尚未开始十张采集。</div>
<p class="hint">预览显示与高清原图相同的取景范围。放好手掌后可立即按拍摄；连续拍十张时不用移开手或手臂。即使暂时没有检测到掌心，原图也会保存。拍后检查裁图和纹线。</p></section>
<section class="card"><h2>采集标签</h2>
<label for="subject">受试编号</label><input id="subject" placeholder="例如 p01" maxlength="40" pattern="[A-Za-z0-9_-]+" autocomplete="off">
<div class="row"><div><label for="hand">哪只手</label><select id="hand"><option value="" selected>请选择</option><option value="right">右手</option><option value="left">左手</option></select></div>
<div><label for="background">背景</label><select id="background"><option value="" selected>请选择</option><option value="existing">现有背景</option><option value="white">白纸</option><option value="other">其他</option></select></div></div>
<label for="distance">镜头到掌心距离（厘米，可留空）</label><input id="distance" type="number" min="5" max="100" step="0.5" inputmode="decimal">
<label for="notes">备注（可选）</label><textarea id="notes" maxlength="200" placeholder="例如：固定支架、IR 灯、手掌重新放置后采集"></textarea>
<button id="start">开始十张采集</button><button id="capture" disabled>开始后可拍摄</button><button id="abandon" class="secondary" hidden>放弃本组</button>
<a id="download" class="download" href="#" hidden>下载本组十张照片 ZIP</a><button id="delete-current" class="danger" hidden>删除本组照片</button><div id="state">先填写标签并开始采集。</div>
<p class="hint">一组固定同一只手、背景、距离和灯光。每张单独保存高清原图、拍摄前的预览帧与曝光／增益参数。</p></section>
<section class="card wide"><h2>拍后检查 · 本组照片</h2><div id="samples"></div><p id="summary" class="hint">尚无照片。</p>
<div id="diagnostics" class="diagnostics" hidden><figure><img id="roi-image" alt="从高清原图重新定位得到的掌心小图"><figcaption>128×128 掌心裁图：拍后从高清原图重新定位；查看手指、背景和位置偏移。实时验证仍使用预览帧。</figcaption></figure><figure><img id="detail-image" alt="掌心 512×512 原始像素局部"><figcaption>512×512 原始细节：查看纹线、反光和对焦。</figcaption></figure></div>
<div class="links"><a id="roi-link" href="#" hidden target="_blank">放大掌心裁图</a><a id="detail-link" href="#" hidden target="_blank">放大原始细节</a><a id="full-link" href="#" hidden target="_blank">打开完整原图</a><a id="meta-link" href="#" hidden target="_blank">查看拍摄参数</a></div>
<p class="hint">高清原图预览：点击掌心，下面会显示该位置周围的原始像素局部。</p><img id="shot" alt="最近拍摄的高清照片" hidden>
  <canvas id="crop" width="512" height="512"></canvas></section>
<section class="card wide"><h2>已保存掌纹采集组</h2><p class="hint">每一行是一个采集文件夹，按受试编号和左右手管理。删除只会删除该组原图、ROI、metadata、session manifest 和对应 ZIP 内容。</p><div id="session-list" class="session-list"><div class="empty-sessions">正在读取已保存采集组…</div></div></section></main>
<script>
const live=document.getElementById('live'),shot=document.getElementById('shot'),crop=document.getElementById('crop');
const state=document.getElementById('state'),capture=document.getElementById('capture'),start=document.getElementById('start'),abandon=document.getElementById('abandon'),deleteCurrent=document.getElementById('delete-current');
const readiness=document.getElementById('readiness'),progress=document.getElementById('progress'),download=document.getElementById('download');
const formIds=['subject','hand','background','distance','notes'];let lastPreview=null,busy=false,activeSession=null,sampleSignature='';
async function refreshPreview(){try{const r=await fetch('/frame.jpg?t='+Date.now(),{cache:'no-store'});if(r.ok){const next=URL.createObjectURL(await r.blob());live.onload=()=>{if(lastPreview)URL.revokeObjectURL(lastPreview);lastPreview=next};live.src=next}}catch(e){}setTimeout(refreshPreview,250)}
refreshPreview();
function showSample(d){if(!d||!d.sample_id)return;const base='/api/collection/sample/'+encodeURIComponent(d.sample_id);
shot.src=base+'/full.jpg?t='+Date.now();shot.hidden=false;
const full=document.getElementById('full-link'),meta=document.getElementById('meta-link');full.href=base+'/full.jpg';meta.href=base+'/metadata.json';full.hidden=false;meta.hidden=false;
const diagnostics=document.getElementById('diagnostics'),roiLink=document.getElementById('roi-link'),detailLink=document.getElementById('detail-link');diagnostics.hidden=!d.roi_available;roiLink.hidden=!d.roi_available;detailLink.hidden=!d.roi_available;
if(d.roi_available){roiLink.href=base+'/roi_128.png';detailLink.href=base+'/palm_detail_512.jpg';document.getElementById('roi-image').src=roiLink.href+'?t='+Date.now();document.getElementById('detail-image').src=detailLink.href+'?t='+Date.now()}
const exposure=d.exposure_ms==null?'':(' · 曝光 '+Number(d.exposure_ms).toFixed(1)+' ms');const gain=d.analogue_gain==null?'':(' · 增益 '+Number(d.analogue_gain).toFixed(2));
document.getElementById('summary').textContent=d.sample_id+' · '+d.width+'×'+d.height+' · '+d.subject+' / '+d.hand+' · '+d.background+exposure+gain;
}
function renderSamples(ids){const signature=ids.join(',');if(signature===sampleSignature)return;sampleSignature=signature;const list=document.getElementById('samples');list.replaceChildren();ids.forEach((id,index)=>{const button=document.createElement('button');button.textContent=`查看第 ${index+1} 张`;button.onclick=async()=>{try{const r=await fetch('/api/collection/sample/'+encodeURIComponent(id)+'/metadata.json');if(!r.ok)throw Error('无法读取照片');showSample(await r.json())}catch(e){state.textContent=e.message}};list.append(button)})}
function handLabel(hand){return hand==='left'?'左手':hand==='right'?'右手':hand||'未知手别'}
async function refreshSessions(){const list=document.getElementById('session-list');try{const r=await fetch('/api/collection/sessions?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('无法读取采集组');const d=await r.json(),sessions=d.sessions||[];list.replaceChildren();if(!sessions.length){const empty=document.createElement('div');empty.className='empty-sessions';empty.textContent='暂无已保存采集组。';list.append(empty);return}for(const session of sessions){const row=document.createElement('div');row.className='session-row';const info=document.createElement('div');info.className='session-info';const title=document.createElement('div');title.className='session-title';title.textContent=`${session.subject||'未命名'} · ${handLabel(session.hand)}`;const meta=document.createElement('div');meta.className='session-meta';meta.textContent=`${session.sample_count}/${session.total} 张 · ${session.background||'未知背景'} · ${session.session_id}`;info.append(title,meta);const actions=document.createElement('div');if(session.phase==='complete'){const link=document.createElement('a');link.className='download';link.href='/api/collection/session/'+encodeURIComponent(session.session_id)+'.zip';link.textContent='下载 ZIP';link.target='_blank';actions.append(link)}const remove=document.createElement('button');remove.className='danger';remove.textContent='删除文件夹';remove.onclick=()=>deleteSession(session);actions.append(remove);row.append(info,actions);list.append(row)}}catch(e){list.textContent=e.message}}
async function deleteSession(session){const label=`${session.subject||'未命名'} · ${handLabel(session.hand)} · ${session.sample_count}/${session.total} 张`;if(!confirm(`确认删除采集文件夹？\n${label}\n\n会删除该组原图、ROI、metadata 和 session 文件，不能恢复。`))return;busy=true;deleteCurrent.disabled=true;try{const r=await fetch('/api/collection/delete-session',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:session.session_id})});const d=await r.json();if(!r.ok)throw Error(d.message||'删除失败');if(activeSession===session.session_id){activeSession=null;sampleSignature='';renderSamples([]);shot.hidden=true;document.getElementById('diagnostics').hidden=true;document.getElementById('summary').textContent='尚无照片。';for(const id of ['full-link','roi-link','detail-link','meta-link'])document.getElementById(id).hidden=true}state.textContent=`已删除 ${d.deleted_samples} 张照片。`;await refreshState();await refreshSessions()}catch(e){state.textContent='删除失败：'+e.message}finally{busy=false;deleteCurrent.disabled=false}}
fetch('/api/collection/latest').then(r=>r.ok?r.json():null).then(showSample).catch(()=>{});
function lockForm(locked){for(const id of formIds)document.getElementById(id).disabled=locked}
async function refreshState(){try{const r=await fetch('/api/status?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('状态暂不可用');const d=await r.json(),b=d.highres_batch||{phase:'idle',captured:0,total:10};
if(b.session_id&&activeSession!==b.session_id){activeSession=b.session_id;for(const id of ['subject','hand','background'])document.getElementById(id).value=b[id]||'';document.getElementById('distance').value=b.distance_cm==null?'':b.distance_cm;document.getElementById('notes').value=b.notes||'';if(!(b.sample_ids||[]).length){shot.hidden=true;document.getElementById('diagnostics').hidden=true;document.getElementById('summary').textContent='尚无本组照片。';for(const id of ['full-link','roi-link','detail-link','meta-link'])document.getElementById(id).hidden=true}}
const phase=b.phase||'idle',tracking=d.roi_status==='tracking';
renderSamples(b.sample_ids||[]);
lockForm(phase==='await_hand');start.disabled=busy||(phase!=='idle'&&phase!=='complete');start.textContent=phase==='complete'?'开始新一组十张':'开始十张采集';
abandon.hidden=phase!=='await_hand';abandon.disabled=busy;
capture.disabled=busy||!b.can_capture;capture.textContent=b.can_capture?`立即拍第 ${b.next_sample}/10 张 · 3280×2464`:'开始后可拍摄';
 download.hidden=phase!=='complete';if(phase==='complete')download.href='/api/collection/session/'+encodeURIComponent(b.session_id)+'.zip';deleteCurrent.hidden=!b.session_id||!b.captured;deleteCurrent.disabled=busy;
progress.textContent=phase==='idle'?'尚未开始十张采集。':`本组已拍 ${b.captured}/10 张`;
readiness.className='readiness';
if(phase==='idle'){readiness.textContent='填写标签，点击开始十张采集。'}
else if(phase==='complete'){readiness.textContent='十张已完成，可以下载整组照片。';readiness.classList.add('ready')}
else if(b.can_capture&&tracking){readiness.textContent=`已检测到手掌，可直接拍第 ${b.next_sample} 张；无需移开手。`;readiness.classList.add('ready')}
else if(b.can_capture){readiness.textContent=`可直接拍第 ${b.next_sample} 张。当前未定位掌心，原图仍会保存，但可能没有自动裁图。`;readiness.classList.add('wait')}
}catch(e){capture.disabled=true;readiness.textContent='相机状态暂不可用，请稍后再试。';readiness.className='readiness wait'}}
refreshState();setInterval(refreshState,400);refreshSessions();setInterval(refreshSessions,3000);
start.onclick=async()=>{const subject=document.getElementById('subject').value.trim(),hand=document.getElementById('hand').value,background=document.getElementById('background').value;
if(!/^[A-Za-z0-9_-]{1,40}$/.test(subject)){state.textContent='请填写英文字母、数字、_ 或 - 组成的受试编号。';return}if(!hand||!background){state.textContent='请先选择哪只手和背景。';return}
busy=true;start.disabled=true;try{const r=await fetch('/api/collection/start-batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({subject,hand,background,distance_cm:document.getElementById('distance').value,notes:document.getElementById('notes').value,client_time:new Date().toISOString()})});const d=await r.json();if(!r.ok)throw Error(d.message||'开始失败');state.textContent='本组已开始。放好手掌，直接拍第 1 张。'}catch(e){state.textContent='无法开始：'+e.message}finally{busy=false;await refreshState()}};
capture.onclick=async()=>{busy=true;capture.disabled=true;state.textContent='正在拍摄高清原图，请把手掌留在画面中…';try{const r=await fetch('/api/collection/capture-batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client_time:new Date().toISOString()})});const d=await r.json();if(!r.ok)throw Error(d.message||'拍摄失败');showSample(d);state.textContent=d.phase==='complete'?'第 10 张已保存。可下载整组照片。':`第 ${d.sample_index} 张已保存。手可以留在画面中，继续拍下一张。`;if(!d.roi_available)state.textContent+=' 这张未能生成掌心裁图；原图已保存，请检查手掌位置。'}catch(e){state.textContent='拍摄失败：'+e.message}finally{busy=false;await refreshState()}};
abandon.onclick=async()=>{if(!confirm('放弃当前这组？已拍的照片会保留在树莓派上，新的十张需要重新开始。'))return;busy=true;abandon.disabled=true;try{const r=await fetch('/api/collection/abandon-batch',{method:'POST'});const d=await r.json();if(!r.ok)throw Error(d.message||'放弃失败');activeSession=null;renderSamples([]);shot.hidden=true;document.getElementById('diagnostics').hidden=true;document.getElementById('summary').textContent='尚无本组照片。';for(const id of ['full-link','roi-link','detail-link','meta-link'])document.getElementById(id).hidden=true;state.textContent='本组已放弃。请核对标签后开始新一组。'}catch(e){state.textContent='无法放弃：'+e.message}finally{busy=false;await refreshState()}};
deleteCurrent.onclick=async()=>{if(!activeSession)return;const sessions=await fetch('/api/collection/sessions?t='+Date.now(),{cache:'no-store'}).then(r=>r.json()).catch(()=>({sessions:[]}));const session=(sessions.sessions||[]).find(item=>item.session_id===activeSession);if(session)await deleteSession(session)};
shot.onclick=e=>{if(!shot.naturalWidth)return;const box=shot.getBoundingClientRect();const x=(e.clientX-box.left)/box.width*shot.naturalWidth,y=(e.clientY-box.top)/box.height*shot.naturalHeight;
const size=Math.min(512,shot.naturalWidth,shot.naturalHeight),sx=Math.max(0,Math.min(shot.naturalWidth-size,x-size/2)),sy=Math.max(0,Math.min(shot.naturalHeight-size,y-size/2));
const ctx=crop.getContext('2d');ctx.clearRect(0,0,512,512);ctx.imageSmoothingEnabled=false;ctx.drawImage(shot,sx,sy,size,size,0,0,512,512)};
</script></body></html>"""
