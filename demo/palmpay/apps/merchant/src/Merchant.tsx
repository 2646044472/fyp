import { Enrollment } from './Enrollment'
import { Button } from '../../../packages/ui/button'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMachine } from '@xstate/react'
import { ArrowRight, ArrowUpRight, ChartNoAxesColumnIncreasing, Check, CircleAlert, Coffee, Grid2X2, Hand, Minus, Plus, ReceiptText, Scan, Search, Settings as SettingsIcon, ShoppingBag, SlidersHorizontal, Trash2 } from 'lucide-react'
import { api, ApiError, requestKey } from '../../../packages/api-client'
import { Brand, Dialog, money, stamp } from '../../../packages/ui'
import { useEvents } from '../../../packages/ui/hooks'
import { Receipt } from '../../../packages/ui/receipt'
import type { Merchant as Register, Order, Payment, Product } from '../../../packages/shared-types'
import { paymentMachine } from './payment'

function MerchantLogin({ error }: { error?: Error | null }) {
  const [message,setMessage]=useState(''), [busy,setBusy]=useState(false)
  const query=useQueryClient()
  async function signIn(event:FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data=new FormData(event.currentTarget)
    setBusy(true);setMessage('')
    try {await api('/merchant/session','POST',{key:data.get('key')});await query.invalidateQueries({queryKey:['merchant']})}
    catch(error){setMessage((error as Error).message)}
    finally{setBusy(false)}
  }
  return <main className="register-login"><Brand merchant/><div className="register-login-icon"><Coffee size={34}/></div><h1>CKLC Coffee</h1><p>Sign in to open Register 01.</p><form className="form" onSubmit={signIn}>
    <label>Operator access key<input name="key" type="password" required autoComplete="current-password"/></label>
    {(message || (error && !(error instanceof ApiError && error.status===401))) && <p role="alert" className="error">{message || 'The register could not connect.'}</p>}
    <Button variant="default" disabled={busy}>Open register <ArrowRight size={18}/></Button></form><Link className="quiet" to="/wallet">Open Palm Wallet <ArrowUpRight size={16}/></Link></main>
}

function PaymentPanel({ payment, state, demo, station, busy, change, retry, close }: {
  payment:Payment;state:unknown;demo:boolean;station:boolean;busy:boolean;
  change:(kind:'approve'|'decline'|'cancel'|'station',email?:string)=>void;retry:()=>void;close:()=>void
}) {
  const [email,setEmail]=useState('')
  const [seconds,setSeconds]=useState(0)
  useEffect(()=>{
    const tick=()=>setSeconds(Math.max(0,Math.ceil(payment.expires_at-Date.now()/1000)))
    tick();const timer=window.setInterval(tick,1000);return ()=>window.clearInterval(timer)
  },[payment.expires_at])
  const waiting=state==='waiting', paid=state==='paid'
  return <div className="payment-panel">
    {paid ? <><div className="row paid-caption"><Check size={20}/> Payment successful</div><Receipt payment={payment}/><Button variant="default" className="full" onClick={close}>New order <Plus size={18}/></Button></> : <>
      <div className="terminal-illustration">{waiting?<><Scan size={102} strokeWidth={0.85}/><Hand size={46} strokeWidth={1.2}/></>:<CircleAlert size={38}/>}</div>
      <h2>{waiting?'Waiting for palm':payment.status==='cancelled'?'Order cancelled':payment.status==='expired'?'Payment expired':'Payment failed'}</h2>
      <strong className="checkout-total"><small>MOP</small> {money(payment.amount)}</strong>
      <div className="payment-lines">{payment.items.map(item=><div className="row" key={item.product_id}><span>{item.quantity} × {item.name}</span><b>{money(item.price*item.quantity)}</b></div>)}</div>
      {waiting ? <><p>Register 01 · {seconds}s remaining</p>{demo && <form className="form simulator" onSubmit={event=>{event.preventDefault();change('approve',email)}}>
        <h3>Demo authorization</h3><label>Enrolled wallet email<input type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label><Button variant="default" className="full" disabled={busy || seconds===0}>Simulate approval</Button>
        <button type="button" className="secondary full" disabled={busy || seconds===0} onClick={()=>change('decline')}>Simulate decline</button>
      </form>}{station && <><p>Hold your registered palm above the camera and keep it steady.</p><Button className="full" disabled={busy || seconds===0} onClick={()=>change('station')}>{busy?'Checking palm…':'Start palm verification'}</Button></>}<Button variant="ghost" className="full" onClick={()=>change('cancel')}>Cancel payment</Button></> :
      <><p role="status">{payment.reason}</p>{payment.status!=='cancelled' && <><Button variant="default" className="full" disabled={busy} onClick={retry}>Retry payment</Button><Button variant="secondary" className="full" disabled={busy} onClick={()=>change('cancel')}>Cancel order</Button></>}<Button variant="ghost" className="full" onClick={close}>New order</Button></>}
    </>}
  </div>
}

function Products({ products, busy, send }: {products:Product[];busy:boolean;send:(id:string|undefined,data:Omit<Product,'id'|'image'>)=>void}) {
  const [editing,setEditing]=useState<Product | 'new' | null>(null)
  const item=editing==='new'?undefined:editing
  function submit(event:FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form=new FormData(event.currentTarget)
    send(item?.id,{name:String(form.get('name')).trim(),category:form.get('category') as Product['category'],price:Math.round(Number(form.get('price'))*100),available:form.get('available')==='on'})
    setEditing(null)
  }
  return <section className="register-page"><div className="row"><h1>Products</h1><Button variant="default" onClick={()=>setEditing('new')}><Plus size={18}/> Add product</Button></div><div className="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Price</th><th>Availability</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{products.map(p=><tr key={p.id}><td>{p.name}</td><td>{p.category}</td><td>MOP {money(p.price)}</td><td>{p.available?'Available':'Hidden'}</td><td><Button variant="ghost" onClick={()=>setEditing(p)}>Edit</Button></td></tr>)}</tbody></table></div>
  {editing && <Dialog title={item?'Edit product':'Add product'} onClose={()=>setEditing(null)}><form className="form" onSubmit={submit}><label>Name<input name="name" required maxLength={80} defaultValue={item?.name}/></label><label>Category<select name="category" defaultValue={item?.category}><option>Coffee</option><option>Non-coffee</option></select></label><label>Price (MOP)<input name="price" type="number" required min=".01" max="10000" step=".01" defaultValue={item?item.price/100:undefined}/></label><label className="check"><input name="available" type="checkbox" defaultChecked={item?.available??true}/> Available at checkout</label><Button variant="default" disabled={busy}>Save product</Button></form></Dialog>}
  </section>
}

type Draft = { cart: Record<string,number>; orderKey: string; paymentKey: string }
function loadDraft(): Draft {
  try {
    const saved = sessionStorage.getItem('palm.draft')
    if (saved) return JSON.parse(saved) as Draft
  } catch {
    // A blocked or invalid browser draft can be replaced.
  }
  return {cart:{},orderKey:requestKey(),paymentKey:requestKey()}
}

const day = (date:Date) => new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Macau',dateStyle:'short'}).format(date)

function Overview({orders}: {orders:Order[]}) {
  const paid=orders.filter(order=>order.payment?.paid_at && day(new Date(order.payment.paid_at))===day(new Date()))
  const revenue=paid.reduce((sum,order)=>sum+order.total,0)
  return <section className="register-page"><h1>Overview</h1><p>Today at CKLC Coffee · Macau time</p><div className="metrics">{[['Revenue','MOP '+money(revenue)],['Paid orders',paid.length],['Average order','MOP '+money(paid.length?Math.round(revenue/paid.length):0)]].map(([label,value])=><article className="surface" key={label}><p>{label}</p><strong>{value}</strong></article>)}</div></section>
}

export default function Merchant() {
  const query=useQueryClient(), nav=useNavigate()
  const session=useQuery({queryKey:['merchant','session'],queryFn:()=>api<Register>('/merchant/session')})
  const productQuery=useQuery({queryKey:['merchant','products'],queryFn:()=>api<Product[]>('/merchant/products'),enabled:!!session.data})
  const ordersQuery=useQuery({queryKey:['merchant','orders'],queryFn:()=>api<Order[]>('/merchant/orders'),enabled:!!session.data,refetchInterval:5000})
  const stationStatus=useQuery({
    queryKey:['merchant','station-status'],
    queryFn:()=>api<{connected:boolean;message:string}>('/station/status'),
    enabled:!!session.data?.station, refetchInterval:4000,
  })
  const products=productQuery.data??[], orders=ordersQuery.data??[]
  const [draft,setDraft]=useState(loadDraft), [category,setCategory]=useState('All'), [search,setSearch]=useState('')
  const {cart,orderKey,paymentKey}=draft
  useEffect(()=>{sessionStorage.setItem('palm.draft',JSON.stringify(draft))},[draft])
  const [status,setStatus]=useState('All'), [error,setError]=useState(''), [notice,setNotice]=useState(''), [busy,setBusy]=useState(false), [install,setInstall]=useState(false)
  const [intentId,setIntentId]=useState(()=>localStorage.getItem('palm.activeIntent')||'')
  const [machine,send]=useMachine(paymentMachine)
  const inflight=useRef(false)
  const payment=machine.context.payment
  useEvents('merchant',!!session.data)
  const getIntent=useQuery({queryKey:['merchant','payment',intentId],queryFn:()=>api<Payment>('/payments/'+intentId),enabled:!!session.data&&!!intentId,refetchInterval:payment?.status==='paid'?false:1500})
  useEffect(()=>{if(getIntent.data)send({type:'SYNC',payment:getIntent.data})},[getIntent.data,send])
  function sync(payment:Payment) {
    localStorage.setItem('palm.activeIntent',payment.id);setIntentId(payment.id)
    query.setQueryData(['merchant','payment',payment.id],payment)
    send({type:'SYNC',payment})
  }
  async function action(fn:()=>Promise<unknown>) {
    if(inflight.current)return
    inflight.current=true;setBusy(true);setError('');setNotice('')
    try{await fn();await query.invalidateQueries({queryKey:['merchant']})}
    catch(error){setError((error as Error).message)}
    finally{inflight.current=false;setBusy(false)}
  }
  function reset() {
    send({type:'RESET'});setIntentId('');localStorage.removeItem('palm.activeIntent')
    setDraft({cart:{},orderKey:requestKey(),paymentKey:requestKey()});setError('')
  }
  function adjust(id:string,by:number) {
    setDraft(previous=>({cart:{...previous.cart,[id]:Math.max(0,Math.min(99,(previous.cart[id]||0)+by))},orderKey:requestKey(),paymentKey:requestKey()}))
  }
  function checkout() {
    void action(async()=>{
      const order=await api<Order>('/merchant/orders','POST',{items:cartProducts.map(x=>({product_id:x.id,quantity:cart[x.id]}))},orderKey)
      sync(await api<Payment>('/payments','POST',{order_id:order.id},paymentKey))
    })
  }
  function change(kind:'approve'|'decline'|'cancel'|'station',email?:string) {
    if(!payment)return
    if(kind==='cancel'){
      setError('')
      void api<Payment>('/payments/'+payment.id+'/cancel','POST').then(sync).catch(error=>setError(error.message))
      return
    }
    if(kind==='station'){
      void action(async()=>sync(await api<Payment>('/station/payments/'+payment.id+'/authorize','POST')))
      return
    }
    void action(async()=>sync(await api<Payment>('/dev/payments/'+payment.id+'/simulate','POST',{email:email||'',outcome:kind})))
  }
  function retry() {
    if(!payment)return
    void action(async()=>sync(await api<Payment>('/payments','POST',{order_id:payment.order_id},requestKey())))
  }
  const cartProducts=products.filter(p=>cart[p.id]>0)
  const count=cartProducts.reduce((sum,p)=>sum+cart[p.id],0)
  const displayedCount=payment?payment.items.reduce((sum,item)=>sum+item.quantity,0):count
  const total=cartProducts.reduce((sum,p)=>sum+p.price*cart[p.id],0)
  if(session.isPending)return <main className="register-login"><Brand merchant/><p role="status">Connecting to the register…</p></main>
  if(!session.data)return <MerchantLogin error={session.error}/>
  const register=session.data
  const menu=products.filter(p=>p.available && (category==='All'||p.category===category) && p.name.toLowerCase().includes(search.toLowerCase()))
  return <div className="merchant-shell">
    <aside className="merchant-sidebar"><Link to="/merchant"><Brand merchant/></Link><nav aria-label="Merchant">{[[Grid2X2,'Checkout',''],[Hand,'Enroll customer','enroll'],[ReceiptText,'Orders','orders'],[SlidersHorizontal,'Products','products'],[ChartNoAxesColumnIncreasing,'Overview','overview'],[SettingsIcon,'Settings','settings']].map(([Icon,label,path])=>{const ItemIcon=Icon as typeof Grid2X2;return <NavLink key={String(label)} end={!path} to={'/merchant'+(path?'/'+path:'')}><ItemIcon size={19}/><span>{String(label)}</span></NavLink>})}</nav><div className="sidebar-foot"><Coffee size={18}/><div><b>{register.merchant}</b><small>{register.terminal}</small></div></div></aside>
    <div className="workspace"><header className="merchant-header"><div><b>{register.merchant}</b><span>{register.terminal}</span></div><div className="header-right"><Button variant="ghost" onClick={()=>setInstall(true)}>Open wallet <ArrowUpRight size={16}/></Button><span className="online"><i/>{ordersQuery.isError?'Reconnecting':register.station?(stationStatus.isError||stationStatus.data?.connected===false?'Station offline':stationStatus.data?.connected?'Station connected':'Checking station'):'Online'}</span></div></header>
    {error && <p role="alert" className="error register-message">{error}</p>}{notice && <p role="status" className="register-message">{notice}</p>}
    <Routes>
      <Route index element={<div className="checkout"><section className="catalogue"><div className="eyebrow">REGISTER CHECKOUT</div><h1>Menu</h1>
        <div className="catalogue-tools"><div className="tabs" aria-label="Categories">{['All','Coffee','Non-coffee'].map(value=><button key={value} className={value===category?'selected':''} onClick={()=>setCategory(value)} aria-pressed={value===category}>{value}</button>)}</div>
        <label className="search"><Search size={18}/><input aria-label="Search menu" placeholder="Search menu" value={search} onChange={e=>setSearch(e.target.value)}/></label></div>
        <div className="product-grid">{menu.map(product=><button className="product-card" key={product.id} onClick={()=>adjust(product.id,1)} disabled={busy||!!intentId}><div className="product-photo">{product.image?<img src={product.image} alt="" onError={e=>e.currentTarget.hidden=true}/>:<Coffee size={38}/>}</div><div className="product-text"><div><b>{product.name}</b><small>MOP {money(product.price)}</small></div><span className="product-plus"><Plus size={17}/></span></div></button>)}</div>
        {!menu.length && <p role="status">{productQuery.isPending?'Loading menu…':productQuery.isError?'Could not load products.':'No products match.'}</p>}
      </section><aside className="cart" aria-label="Current order">
        <div className="cart-head row"><h2>Current order</h2><span className="cart-count">{displayedCount} {displayedCount===1?'item':'items'}</span></div>
        {payment ? <PaymentPanel payment={payment} state={machine.value} demo={register.demo} station={register.station} busy={busy} change={change} retry={retry} close={reset}/> : intentId ? <div className="cart-empty"><p>{getIntent.isError?'Unable to recover this payment.':'Recovering payment…'}</p><Button variant="secondary" onClick={()=>void getIntent.refetch()}>Reconnect</Button>{getIntent.error instanceof ApiError&&getIntent.error.status===404&&<Button variant="ghost" onClick={reset}>Dismiss</Button>}</div> : <>
          <div className="cart-body">{count===0?<div className="cart-empty"><span><ShoppingBag size={27} strokeWidth={1.5}/></span><h3>Your order is empty</h3><p>Tap a drink to add it to the order.</p></div>:cartProducts.map(p=><div className="cart-line" key={p.id}><div><b>{p.name}</b><small>MOP {money(p.price)}</small></div><div className="quantity"><button aria-label={'Remove one '+p.name} disabled={busy} onClick={()=>adjust(p.id,-1)}><Minus size={17}/></button><output>{cart[p.id]}</output><button aria-label={'Add one '+p.name} disabled={busy} onClick={()=>adjust(p.id,1)}><Plus size={17}/></button></div></div>)}</div>
          <div className="cart-foot"><div className="row"><span>Total <small>· MOP</small></span><strong className="checkout-total">{money(total)}</strong></div><Button variant="default" className="full" disabled={!count||busy} onClick={checkout}><Hand size={19}/> Pay with palm <ArrowRight size={18}/></Button><Button variant="ghost" className="full" disabled={!count||busy} onClick={reset}><Trash2 size={16}/> Clear order</Button></div>
        </>}
        <p className="cart-note">{register.demo?'Demo register · All payments use simulated funds':register.station?'FPN + C E10 · Simulated funds':'PalmPay register · Simulated funds'}</p>
      </aside></div>}/>
      <Route path="enroll" element={<Enrollment demo={register.demo}/>}/>
      <Route path="orders" element={<section className="register-page"><h1>Orders</h1><div className="tabs">{['All','Pending','Paid','Failed','Cancelled'].map(value=><button key={value} onClick={()=>setStatus(value)} className={status===value?'selected':''} aria-pressed={status===value}>{value}</button>)}</div><div className="table-wrap"><table><thead><tr><th>Order</th><th>Created</th><th>Total</th><th>Status</th><th>Payment</th></tr></thead><tbody>{orders.filter(order=>status==='All'||order.status===status.toLowerCase()).map(order=><tr key={order.id}><td>#{order.id.slice(0,6).toUpperCase()}</td><td>{stamp(order.created_at)}</td><td>MOP {money(order.total)}</td><td className={'order-'+order.status}>{order.status}</td><td>{order.payment ? <Button variant="ghost" onClick={()=>{sync(order.payment!);nav('/merchant')}}>{order.status==='paid'?'View receipt':'View payment'}</Button> : <Button variant="ghost" disabled={busy} onClick={()=>void action(async()=>{sync(await api<Payment>('/payments','POST',{order_id:order.id},requestKey()));nav('/merchant')})}>Start payment</Button>}</td></tr>)}</tbody></table>{!orders.length&&<p className="empty-table">{ordersQuery.isError?'Could not load orders.':'Orders will appear here.'}</p>}</div></section>}/>
      <Route path="products" element={<Products products={products} busy={busy} send={(id,data)=>void action(()=>api('/merchant/products'+(id?'/'+id:''),id?'PUT':'POST',data))}/>}/>
      <Route path="overview" element={<Overview orders={orders}/>}/>
      <Route path="settings" element={<section className="register-page"><h1>Settings</h1><div className="settings-grid"><section className="surface stack"><h2>Register</h2>{register.station&&<><p role="status">{stationStatus.data?.message??'Checking station connection…'}</p><Button variant="secondary" onClick={()=>void stationStatus.refetch()}>Check station connection</Button></>}<p>{register.merchant} · {register.terminal}</p><p>{register.demo?'Demo authorization is connected.':register.station?'FPN + C E10 camera verification is configured.':'Demo authorization is disabled.'}</p><Button variant="secondary" disabled={busy} onClick={()=>void action(async()=>{await api('/auth/logout/merchant','POST');reset();query.removeQueries({queryKey:['merchant','orders']})})}>Sign out</Button></section><section className="surface stack"><h2>Customer enrollment</h2><p>Register a customer and capture their palm at this counter.</p><Link className="secondary" to="/merchant/enroll">Enroll customer</Link></section></div></section>}/>
      <Route path="*" element={<Navigate to="/merchant" replace/>}/>
    </Routes></div>
    {install&&<Dialog title="Open Palm Wallet" onClose={()=>setInstall(false)}><p>Scan with your phone on the same network.</p><img className="wallet-qr" src={'/api/wallet-qr?url='+encodeURIComponent(location.origin+'/wallet')} alt="QR code for Palm Wallet"/><a className="secondary full" href="/wallet" target="_blank" rel="noreferrer">Open in a new tab <ArrowUpRight size={16}/></a></Dialog>}
  </div>
}

