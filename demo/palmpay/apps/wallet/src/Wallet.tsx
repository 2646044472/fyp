import { Button } from '../../../packages/ui/button'
import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, useReducedMotion } from 'motion/react'
import { ArrowDownLeft, ArrowRight, Check, ChevronRight, Coffee, Hand, House, Plus, ReceiptText, Scan, Search, ShieldCheck, UserRound, Wallet as WalletIcon } from 'lucide-react'
import { api, ApiError, requestKey } from '../../../packages/api-client'
import { Brand, Dialog, money, stamp } from '../../../packages/ui'
import { useEvents } from '../../../packages/ui/hooks'
import { Receipt } from '../../../packages/ui/receipt'
import type { Payment, Wallet as WalletData } from '../../../packages/shared-types'

const credentials = z.object({ name:z.string().optional(), email:z.email(), password:z.string().min(8), consent:z.boolean().optional() })
type Entry = z.infer<typeof credentials>

function Welcome() {
  const [error, setError] = useState('')
  const {register, handleSubmit, formState} = useForm<Entry>({ resolver:zodResolver(credentials), defaultValues:{consent:false} })
  const queries = useQueryClient()
  async function submit(data:Entry) {
    setError('')
    try {
      await api('/auth/login','POST',{email:data.email,password:data.password})
      await queries.invalidateQueries({queryKey:['wallet']})
    } catch (error) {setError((error as Error).message)}
  }
  return <main className="welcome"><Brand/><div className="welcome-art" aria-hidden="true"><div><Hand size={76} strokeWidth={1.15}/></div><Scan size={202} strokeWidth={0.55}/></div>
    <p className="eyebrow">PALM WALLET</p><h1>Your palm is<br/>your wallet<span>.</span></h1>
    <p>Sign in to view your balance, add demo funds and see receipts. Create your account and register your palm at the café counter.</p>
    <form className="form" onSubmit={handleSubmit(submit)}>
      <h2>Sign in</h2>
      <label>Email<input type="email" autoComplete="email" required {...register('email')}/></label>
      <label>Password<input type="password" autoComplete="current-password" required minLength={8} maxLength={128} {...register('password')}/></label>
      {(error || Object.keys(formState.errors).length>0) && <p role="alert" className="error">{error || 'Enter a valid email and password.'}</p>}
      <Button disabled={formState.isSubmitting}>Sign in</Button>
    </form>
  </main>
}

function ActivityList({ rows, empty }: { rows:Payment[]; empty:string }) {
  if (!rows.length) return <div className="activity-empty"><ReceiptText size={24}/><p>{empty}</p></div>
  return <div className="activity-list">{rows.map(payment=><Link key={payment.id} to={'/wallet/activity/'+payment.id} className="activity-line"><span className="activity-icon"><Coffee size={18}/></span><span><b>{payment.merchant}</b><small>{stamp(payment.paid_at!)}</small></span><b className="line-amount">−{money(payment.amount)}</b><ChevronRight size={16}/></Link>)}</div>
}

export default function Wallet() {
  const queries=useQueryClient(), nav=useNavigate(), location=useLocation()
  const snapshot=useQuery({queryKey:['wallet','account'],queryFn:()=>api<WalletData>('/wallet')})
  const account=snapshot.data
  const rows=useQuery({queryKey:['wallet','activity'],queryFn:()=>api<Payment[]>('/wallet/transactions'),enabled:!!account,refetchInterval:5000})
  useEvents('wallet',!!account)
  const [error,setError]=useState(''), [busy,setBusy]=useState(false), [search,setSearch]=useState('')
  const [notification,setNotification]=useState<Payment>(), [confirm,setConfirm]=useState(false)
  const last=useRef<string|null|undefined>(undefined), topupKey=useRef(requestKey())
  const reduced=useReducedMotion()
  useEffect(()=>{
    if (!rows.data) return
    const latest = rows.data[0]
    if (latest && last.current!==undefined && latest.id!==last.current) setNotification(latest)
    last.current=latest?.id ?? null
  },[rows.data])
  useEffect(()=>{document.documentElement.lang=account?.locale??'en';return ()=>{document.documentElement.lang='en'}},[account?.locale])
  useEffect(()=>{setError('')},[location.pathname])
  async function action(fn:()=>Promise<unknown>) {
    setBusy(true);setError('')
    try {await fn();await queries.invalidateQueries({queryKey:['wallet']})}
    catch (error) {setError((error as Error).message)}
    finally {setBusy(false)}
  }
  if (snapshot.isPending) return <main className="welcome"><Brand/><p role="status">Opening Palm Wallet…</p></main>
  if (!account) {
    if (snapshot.error instanceof ApiError && snapshot.error.status===401) return <Welcome/>
    return <main className="welcome"><Brand/><h1>Wallet unavailable</h1><Button variant="default" onClick={()=>void snapshot.refetch()}>Reconnect</Button></main>
  }
  const transactions=rows.data??[]
  const chinese=account.locale==='zh-Hant'
  const t=(en:string,zh:string)=>chinese?zh:en
  return <div className="wallet-shell">
    <header className="wallet-header"><Link to="/wallet" aria-label="PalmPay home"><Brand/></Link><Link className="avatar" to="/wallet/profile" aria-label="Profile">{account.name.slice(0,1).toUpperCase()}</Link></header>
    <main className="wallet-main">
      {error && <p className="error" role="alert">{error}</p>}
      <Routes>
        <Route index element={<><div className="wallet-intro"><p className="eyebrow">{t('PALM WALLET','掌紋錢包')}</p><h1>{t('Hello','你好')}, {account.name.split(' ')[0]}.</h1></div>
          <section className="balance"><div className="balance-glyph" aria-hidden="true"><Scan size={145} strokeWidth={0.8}/><Hand size={71} strokeWidth={1}/></div><p>{t('Available balance','可用餘額')}</p><strong><small>MOP</small> {money(account.balance)}</strong><span className="demo-label">{t('Demo funds','模擬資金')}</span></section>
          <button className="secondary topup" onClick={()=>setConfirm(true)}><Plus size={18}/>{t('Add demo funds','增加模擬資金')}</button>

          <div className="row section-title"><h2>{t('Recent activity','近期交易')}</h2><Link to="/wallet/activity">{t('View all','查看全部')} <ArrowRight size={14}/></Link></div>
          <ActivityList rows={transactions.slice(0,3)} empty={rows.isError?'Activity is temporarily unavailable.':t('Your café payments will appear here.','咖啡店付款會顯示在這裡。')}/></>}/>
        <Route path="activity" element={<><h1>{t('Activity','交易紀錄')}</h1><label className="search"><Search size={19}/><input aria-label="Search transactions" placeholder={t('Search transactions','搜尋交易')} value={search} onChange={e=>setSearch(e.target.value)}/></label>
          <ActivityList rows={transactions.filter(p=>[p.merchant,p.reference,...p.items.map(i=>i.name)].join(' ').toLowerCase().includes(search.toLowerCase()))} empty={rows.isError?'Activity is temporarily unavailable.':search?t('No matching transactions.','找不到相符的交易。'):t('Your café payments will appear here.','咖啡店付款會顯示在這裡。')}/></>}/>
        <Route path="activity/:id" element={<><Link className="quiet" to="/wallet/activity">‹ {t('Activity','交易紀錄')}</Link>{transactions.find(p=>p.id===location.pathname.split('/').at(-1)) ? <Receipt payment={transactions.find(p=>p.id===location.pathname.split('/').at(-1))!}/> : <p>{rows.isPending?t('Loading receipt…','正在載入收據…'):t('Receipt unavailable.','無法顯示收據。')}</p>}</>}/>
        <Route path="palm" element={<Navigate to="/wallet" replace/>}/>
        <Route path="profile" element={<><h1>{t('Profile','個人資料')}</h1><section className="surface stack"><div><h2>{account.name}</h2><p>{account.email}</p></div>
          <label>{t('Language','語言')}<select value={account.locale} disabled={busy} onChange={e=>void action(()=>api('/wallet/preferences','PATCH',{locale:e.target.value,consent:account.consent}))}><option value="en">English</option><option value="zh-Hant">繁體中文</option></select></label>

          <Button variant="secondary" disabled={busy} onClick={()=>void action(async()=>{await api('/auth/logout/wallet','POST');last.current=undefined;setNotification(undefined);queries.removeQueries({queryKey:['wallet','activity']});queries.removeQueries({queryKey:['wallet','palm']});nav('/wallet')})}>{t('Sign out','登出')}</Button>
        </section></>}/>
        <Route path="*" element={<Navigate to="/wallet" replace/>}/>
      </Routes>
      {notification && <motion.button className="wallet-toast" role="status" initial={reduced?false:{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:0.22}} onClick={()=>{nav('/wallet/activity/'+notification.id);setNotification(undefined)}}><span className="status-icon"><Check size={19}/></span><span><b>{t('Payment received','付款完成')}</b><small>{notification.merchant} · MOP {money(notification.amount)}</small></span><ChevronRight size={17}/></motion.button>}
    </main>
    <nav className="wallet-nav" aria-label="Wallet">{[[House,'Home','首頁',''],[ReceiptText,'Activity','紀錄','/activity'],[UserRound,'Profile','帳戶','/profile']].map(([Icon,en,zh,path])=>{const ItemIcon=Icon as typeof House;return <NavLink end={!path} key={String(path)} to={'/wallet'+path}><ItemIcon size={21}/>{t(String(en),String(zh))}</NavLink>})}</nav>
    {confirm && <Dialog title={t('Add demo funds','增加模擬資金')} onClose={()=>!busy&&setConfirm(false)}><p><ArrowDownLeft size={15}/> Add MOP 100.00 in simulated funds to your wallet.</p><Button variant="default" className="full" disabled={busy} onClick={()=>void action(async()=>{await api('/wallet/demo-topup','POST',undefined,topupKey.current);topupKey.current=requestKey();setConfirm(false)})}><WalletIcon size={17}/> Add MOP 100.00</Button>{error&&<p className="error" role="alert">{error}</p>}</Dialog>}
  </div>
}

