import { useState, type FormEvent } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../packages/api-client'
import { Button } from '../../../packages/ui/button'

type CustomerSession = {id:string;name:string;hand:string}

export function Enrollment({ demo }: {demo:boolean}) {
  const [create,setCreate]=useState(false)
  const [session,setSession]=useState<CustomerSession|null>(()=>{
    try { return JSON.parse(sessionStorage.getItem('palm.counterEnrollment')||'null') }
    catch { return null }
  })
  const [error,setError]=useState(''), [busy,setBusy]=useState(false)
  const status=useQuery({queryKey:['counter-enrollment',session?.id],
    queryFn:()=>api<{enrolled:boolean}>('/merchant/enrollments/'+session!.id),
    enabled:!!session,refetchInterval:2000})
  async function start(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();setBusy(true);setError('')
    const form=new FormData(event.currentTarget)
    const credentials={email:String(form.get('email')),password:String(form.get('password'))}
    try {
      if(create) await api('/merchant/enrollments/customers','POST',{
        ...credentials,name:form.get('name'),consent:true,
      })
      const result=await api<CustomerSession>('/merchant/enrollments','POST',{
        ...credentials,hand:form.get('hand'),capture_consent:form.get('consent')==='on',
      })
      sessionStorage.setItem('palm.counterEnrollment',JSON.stringify(result));setSession(result)
    } catch(error){setError((error as Error).message)}
    finally{setBusy(false)}
  }
  return <section className="register-page counter-enrollment"><h1>Enroll customer</h1>
    {error&&<p className="error" role="alert">{error}</p>}
    {!session?<><p>The customer signs in at this counter, then registers a palm with the camera.</p>
      <div className="tabs"><button className={!create?'selected':''} onClick={()=>setCreate(false)}>Existing wallet</button><button className={create?'selected':''} onClick={()=>setCreate(true)}>Create customer wallet</button></div>
      <form className="form surface" onSubmit={start}>
        {create&&<label>Customer name<input name="name" required maxLength={80} autoComplete="off"/></label>}
        <label>Customer email<input name="email" type="email" required autoComplete="off"/></label>
        <label>Customer password<input name="password" type="password" required minLength={8} maxLength={128} autoComplete="off"/></label>
        <label>Hand<select name="hand"><option value="left">Left hand</option><option value="right">Right hand</option></select></label>
        <label className="check"><input name="consent" type="checkbox" required/>The customer agrees to this research demo and to palm image and template storage on the local camera station. All funds are simulated.</label>
        <Button disabled={busy}>{busy?'Preparing enrollment…':create?'Create wallet and enroll':'Continue to palm capture'}</Button>
      </form></>:<><div className="row section-title"><h2>{session.name} · {session.hand} hand</h2>
        <Button variant="ghost" onClick={()=>{sessionStorage.removeItem('palm.counterEnrollment');setSession(null);setError('')}}>Back to customers</Button></div>
      {status.data?.enrolled?<div className="enrollment-result" role="status"><h2>Palm registered</h2><p>The palm is linked to this wallet. Start an order in Checkout to pay with the registered hand.</p></div>:
        demo?<div className="surface stack"><p>Demo enrollment uses a simulated identity.</p><Button disabled={busy} onClick={async()=>{setBusy(true);try{await api('/merchant/enrollments/'+session.id+'/simulate','POST');await status.refetch()}catch(error){setError((error as Error).message)}finally{setBusy(false)}}}>Simulate enrollment</Button></div>:
        <><p>Start capture below, hold the selected palm toward the camera, then select and review 10 photos. Confirm and save to link the wallet automatically.</p>
        <iframe className="enrollment-frame" title="Palm capture and review" src={'/api/merchant/enrollments/'+session.id+'/station/'}/>
        {status.isError&&<p className="error">Could not check the wallet link. Reconnect before continuing.</p>}</>}
    </>}
  </section>
}
