import { createState, transition } from './state.mjs';
const el = id => document.getElementById(id);
let state = createState();
let hand = false;
let pending;
let selected;
let identity = { name: 'Alex', hand: 'Right hand' };
let draft = { ...identity };
let lastTick = performance.now();
const canvas = el('palm-canvas');

function paint(target, present, crop = false, gray = false, variant = 0) {
  const ctx = target.getContext('2d');
  const w = target.width, h = target.height;
  ctx.clearRect(0, 0, w, h);
  if (target !== canvas) { ctx.fillStyle = '#183645'; ctx.fillRect(0,0,w,h); }
  ctx.save();
  ctx.translate(w/2, h/2 + h*.035);
  const scale = Math.min(w/560,h/700) * (crop ? 2.7 : .95);
  ctx.scale(scale,scale);
  ctx.rotate((variant%5-2)*.025);
  ctx.globalAlpha = present ? 1 : .15;
  const gradient = ctx.createLinearGradient(-130,0,140,0);
  gradient.addColorStop(0,gray?'#a7b1b2':'#78a3a1');
  gradient.addColorStop(.5,gray?'#e0e3e2':'#c0d6ca');
  gradient.addColorStop(1,gray?'#a0abad':'#719c9c');
  ctx.fillStyle=gradient;ctx.strokeStyle='#b4d3cf';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(-75,290);ctx.lineTo(-83,180);
  ctx.bezierCurveTo(-113,135,-136,99,-160,53);ctx.bezierCurveTo(-188,6,-151,-20,-129,7);
  ctx.lineTo(-97,52);ctx.lineTo(-103,-147);ctx.bezierCurveTo(-103,-188,-63,-190,-60,-150);
  ctx.lineTo(-52,-37);ctx.lineTo(-53,-220);ctx.bezierCurveTo(-53,-261,-10,-263,-8,-222);
  ctx.lineTo(-3,-47);ctx.lineTo(2,-249);ctx.bezierCurveTo(4,-292,47,-292,47,-249);
  ctx.lineTo(45,-46);ctx.lineTo(55,-198);ctx.bezierCurveTo(58,-238,98,-235,97,-193);
  ctx.lineTo(89,91);ctx.bezierCurveTo(89,147,66,166,62,195);ctx.lineTo(66,290);
  ctx.closePath();ctx.fill();ctx.stroke();
  if(present){
    ctx.strokeStyle=gray?'#7e8c8e':'#628e8a';ctx.lineWidth=2.2;
    for(let line=0;line<3;line++){ctx.beginPath();ctx.moveTo(-73+line*14,12+line*43);ctx.bezierCurveTo(-30,-2+line*42,15,40+line*38,69,11+line*45);ctx.stroke();}
    ctx.beginPath();ctx.moveTo(-73,48);ctx.bezierCurveTo(-8,67,-15,116,-30,168);ctx.stroke();
  }
  ctx.restore();
}
function imageFor(id, view='original') {
  const target=document.createElement('canvas');target.width=320;target.height=view==='original'?256:320;
  paint(target,true,view!=='original',view==='model',id);return target.toDataURL('image/png');
}
const images=new Map(Array.from({length:10},(_,index)=>[index+1,imageFor(index+1)]));
function send(event,data){
  const previous=state.phase;state=transition(state,event,data);
  if(state.phase!=='processing'){clearTimeout(pending);pending=null;}
  if(['stop','verify','enroll','error'].includes(event)) hand=false;
  if(previous!==state.phase)lastTick=performance.now();
  render();
}
function message(){
  if(state.phase==='error')return ['!','Let’s reconnect','The simulated camera is unavailable. Retry to restart this session.','Retry camera'];
  if(state.mode==='verify'){
    if(state.phase==='idle')return ['○','Ready when you are','Start the station, then place your palm inside the frame.','Start verification'];
    if(state.phase==='waiting'&&hand)return ['↔','Center your palm','Move your palm into the frame. Remove it, then choose another presenter scenario to continue.',null];
    if(state.phase==='waiting')return ['○','Place your palm','Face your palm toward the camera and bring it inside the frame.',null];
    if(state.phase==='processing')return ['◌','Hold there','Your palm is in position. We’re comparing this presentation.',null];
    if(state.outcome==='match')return ['✓','Match found','This simulated presentation matched the fictional enrollment. Remove your hand to begin again.',null];
    return ['↻','Please try again','This simulated presentation could not be confirmed. Remove your hand, then try once more.',null];
  }
  return {
    idle:['○','Make it your hand','Enter a demo name and hand. We’ll guide a five-second preview, then a full minute of active capture.','Start capture'],
    preview:['○','Find a comfortable position','Place your palm inside the frame. Preview time is separate from active capture.',null],
    capturing:['◌',state.elapsed<20?'Keep your palm facing us':state.elapsed<40?'Try a small angle change':'Return to a comfortable pose','We’re gathering ten synthetic candidate groups. You can pause at any time.',null],
    paused:['Ⅱ','Take your time','Capture is paused. Your active time is preserved. Resume when you’re ready.','Resume capture'],
    review:['✓','Your photos are ready','Review the groups below. Replace anything you remove, then confirm that every group shows the same hand.','Review photo groups'],
    saved:['✓','Demo enrollment saved','Ten synthetic groups are confirmed for this session. The first five represent the enrollment template.','Try verification']
  }[state.phase];
}
function openPhoto(id){
  selected=id;el('dialog-title').textContent=`Photo group ${String(id).padStart(2,'0')}`;
  el('photo-views').replaceChildren(...[['Original','original'],['Color palm crop','color'],['Model input · grayscale','model']].map(([name,view])=>{
    const box=document.createElement('div'),img=new Image(),caption=document.createElement('p');
    img.src=imageFor(id,view);img.alt=`Synthetic ${name}`;img.width=320;img.height=view==='original'?256:320;
    caption.textContent=name;box.append(img,caption);return box;
  }));el('photo-dialog').showModal();
}
function renderPhotos(){
  el('photo-grid').replaceChildren(...state.photos.map(id=>{
    const button=document.createElement('button'),img=new Image(),caption=document.createElement('span'),note=document.createElement('small');
    button.className='photo-card';button.setAttribute('aria-label',`Review photo group ${id}`);
    img.src=images.get(id);img.alt=`Synthetic palm group ${id}`;img.width=320;img.height=256;
    caption.textContent=`Group ${String(id).padStart(2,'0')}`;note.textContent=id<=5?'Template candidate':'Photo record';
    caption.append(note);button.append(img,caption);button.addEventListener('click',()=>openPhoto(id));return button;
  }));
}
function render(){
  const [symbol,title,copy,primary]=message();
  document.querySelector('h1').textContent = state.mode === 'verify' ? 'Palm verification' : 'Enroll your hand';
  el('accelerated').hidden = state.mode !== 'enroll' || !el('speed').checked;
  el('status-symbol').textContent=symbol;el('status-title').textContent=title;el('status-copy').textContent=copy;
  el('primary').hidden=!primary;el('primary').textContent=primary||'';
  el('secondary').hidden=['idle','error','saved'].includes(state.phase);
  el('secondary').textContent=['preview','capturing'].includes(state.phase)?'Pause capture':state.mode==='verify'?'Stop verification':'Cancel capture';
  for(const mode of ['verify','enroll']){const tab=el(`${mode}-tab`);tab.classList.toggle('active',state.mode===mode);if(state.mode===mode)tab.setAttribute('aria-current','page');else tab.removeAttribute('aria-current');}
  el('mode-label').textContent=state.mode==='verify'?'VERIFY A HAND':'ENROLL A HAND';
  el('identity-fields').hidden=state.mode!=='enroll'||state.phase!=='idle';
  el('match-card').hidden=state.mode!=='verify'||state.phase!=='result'||state.outcome!=='match';
  el('matched-name').textContent=`${identity.name} · ${identity.hand}`;
  el('session-note').textContent=state.mode==='verify'?'One presentation, one result. Remove your hand to begin again.':'Session-only demo. No images or enrollment records leave this browser.';
  el('hand-toggle').disabled=state.mode!=='verify'||!['waiting','processing','result'].includes(state.phase);
  el('hand-toggle').textContent=hand?'Remove hand':'Place hand in frame';
  el('capture-progress').hidden=state.mode!=='enroll'||!['preview','capturing','paused','review'].includes(state.phase);
  const preview=state.phase==='preview'||state.resumePhase==='preview';
  el('progress-label').textContent=preview?'Preview':'Active capture';
  el('timer').textContent=preview?`${Math.ceil(state.preview)} / 5 seconds`:`${String(Math.floor(state.elapsed/60)).padStart(2,'0')}:${String(Math.floor(state.elapsed%60)).padStart(2,'0')} / 01:00`;
  el('progress').value=state.elapsed;el('photo-count').textContent=`${state.photos.length} of 10 candidate groups`;
  el('review').hidden=state.phase!=='review';el('replace').hidden=state.photos.length===10;
  el('consent').checked=state.consent;el('save').disabled=!state.consent||state.photos.length!==10;
  const on=['waiting','processing','result','preview','capturing'].includes(state.phase);
  el('frame-state').textContent=on?'Preview active':state.phase==='error'?'Camera unavailable':'Camera off';
  el('camera-instruction').textContent=state.phase==='result'?'Remove your hand to reset':state.phase==='error'?'Retry to reconnect':on?'Palm facing the camera':'Your palm goes here';
  const warning=state.phase==='error'||state.outcome==='unknown';
  el('camera').classList.toggle('success',state.phase==='result'&&state.outcome==='match');el('camera').classList.toggle('warning',warning);
  el('status-symbol').style.background=warning?'#fff0cb':'#e7f4ef';el('status-symbol').style.color=warning?'#795111':'#087c70';
  paint(canvas,hand||['preview','capturing','review'].includes(state.phase));
  if(state.phase==='review')renderPhotos();
}
el('presenter-toggle').addEventListener('click',()=>{const open=el('presenter').hidden;el('presenter').hidden=!open;el('presenter-toggle').setAttribute('aria-expanded',String(open));});
el('speed').addEventListener('change',()=>{el('accelerated').hidden=!el('speed').checked;lastTick=performance.now();});
el('camera-error').addEventListener('click',()=>send('error'));
for(const mode of ['verify','enroll'])el(`${mode}-tab`).addEventListener('click',()=>{if(state.mode===mode)return;if(state.mode==='enroll'&&!['idle','saved','error'].includes(state.phase)&&!confirm('Discard this unsaved demo capture?'))return;send(mode);});
el('hand-toggle').addEventListener('click',()=>{
  if(hand){hand=false;send('remove');return;}
  hand=true;const scenario=el('scenario').value;
  if(scenario==='position'){render();return;}
  send('place');const outcome=scenario==='match'?'match':'unknown';pending=setTimeout(()=>send('result',{outcome}),1400);
});
el('scenario').addEventListener('change',()=>{if(state.phase==='waiting'){hand=false;render();}});
el('primary').addEventListener('click',()=>{
  if(state.phase==='review'){el('review').scrollIntoView({behavior:'instant',block:'start'});el('photo-grid').querySelector('button')?.focus();return;}
  if(state.phase==='saved'){send('verify');return;}
  if(state.phase==='paused'){send('resume');return;}
  if(state.mode==='enroll'&&state.phase==='idle'){
    const name=el('demo-name').value.trim();if(!name){el('demo-name').setCustomValidity('Enter a demo name.');el('demo-name').reportValidity();return;}
    draft={name,hand:el('demo-hand').value};
  }
  send(state.phase==='error'?'retry':'start');
});
el('demo-name').addEventListener('input',()=>el('demo-name').setCustomValidity(''));
el('secondary').addEventListener('click',()=>{
  if(['preview','capturing'].includes(state.phase)){send('pause');return;}
  if(state.mode==='enroll'&&!confirm('Discard this unsaved demo capture?'))return;
  send('stop');
});
el('replace').addEventListener('click',()=>send('replace'));
el('consent').addEventListener('change',event=>send('consent',{value:event.target.checked}));
el('save').addEventListener('click',()=>{send('save');if(state.phase==='saved')identity={...draft};el('status-title').setAttribute('tabindex','-1');el('status-title').focus();});
el('close-dialog').addEventListener('click',()=>el('photo-dialog').close());
el('delete-photo').addEventListener('click',()=>{send('delete',{id:selected});el('photo-dialog').close();el('replace').focus();});
window.addEventListener('beforeunload',event=>{if(state.mode==='enroll'&&!['idle','saved','error'].includes(state.phase)){event.preventDefault();event.returnValue='';}});
setInterval(()=>{const now=performance.now(),seconds=(now-lastTick)/1000;lastTick=now;if(['preview','capturing'].includes(state.phase))send('tick',{seconds:seconds*(el('speed').checked?6:1)});},200);
render();
