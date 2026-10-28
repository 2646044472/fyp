const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map();const element=id=>{if(!elements.has(id))elements.set(id,{value:'',src:'',hidden:false,disabled:false,textContent:''});return elements.get(id)};
let pending=[],calls=[],intervals=new Map(),nextTimer=0;
const context={document:{getElementById:element},Date,URL,console,setTimeout:()=>{},setInterval:f=>{intervals.set(++nextTimer,f);return nextTimer},clearInterval:id=>intervals.delete(id),fetch:async(path,options)=>{if(path.startsWith('/frame'))return {ok:false};if(path==='/api/demo/users')return {json:async()=>({users:[]})};calls.push(path);return new Promise((resolve,reject)=>pending.push({resolve,reject}));}};
vm.createContext(context);vm.runInContext(fs.readFileSync(require('path').join(__dirname,'../demo_page.py'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1],context);
const finish=d=>pending.shift().resolve({ok:true,json:async()=>d});
(async()=>{
 let run=element('identify').onclick();await element('identify').onclick();await element('retry').onclick();assert.equal(calls.length,1);assert(element('retry').disabled);assert(element('user').disabled);for(const fn of intervals.values())fn();assert(element('notice').textContent.includes('秒'));
 finish({status:'MATCH',token:'one',user_id:'p1',display_name:'P1',score:.2,second_score:.3});await run;assert.equal(intervals.size,0);assert(!element('retry').disabled);
 run=element('confirm').onclick();await element('confirm').onclick();await element('retry').onclick();assert.equal(calls.length,2);pending.shift().reject(Error('network'));await run;assert(element('notice').textContent.includes('状态待核实'));assert(!element('notice').textContent.includes('没有扣款'));
 run=element('retry').onclick();finish({status:'CANCELLED'});await run;assert(element('candidate').hidden);
 element('user').value='p1';element('name').value='P1';run=element('enroll').onclick();await element('enroll').onclick();assert.equal(calls.filter(x=>x.endsWith('/enroll')).length,1);finish({display_name:'P1',balance_cents:10000});await run;assert.equal(intervals.size,0);assert(!element('user').disabled);
 console.log('UI interaction checks passed: duplicate actions, busy controls, elapsed timer, uncertain confirmation, cancel, enrollment.');
})().catch(e=>{console.error(e);process.exitCode=1});
