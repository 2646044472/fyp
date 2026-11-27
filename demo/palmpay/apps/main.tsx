import React, { lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ArrowUpRight, Coffee, Wallet as WalletIcon } from 'lucide-react'
import '@fontsource/geist/latin-400.css'
import '@fontsource/geist/latin-500.css'
import '@fontsource/geist/latin-600.css'
import '@fontsource/geist/latin-700.css'

import '../packages/design-tokens/tokens.css'
import './styles.css'
import { Brand } from '../packages/ui'
import { ApiError } from '../packages/api-client'
const Wallet = lazy(() => import('./wallet/src/Wallet'))
const Merchant = lazy(() => import('./merchant/src/Merchant'))

const queries = new QueryClient({ defaultOptions: { queries: { retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 2 } } })
function Landing() {
  return <main className="landing"><Brand/><div className="landing-heading"><h1>Your palm is<br/>your wallet<span>.</span></h1><p>Try a contactless café checkout with simulated funds and palm authorization.</p></div>
    <div className="portals"><Link to="/wallet"><WalletIcon/><b>Palm Wallet</b><ArrowUpRight/></Link><Link to="/merchant"><Coffee/><b>Palm Merchant</b><ArrowUpRight/></Link></div></main>
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><QueryClientProvider client={queries}><BrowserRouter><Suspense fallback={<main className="welcome"><Brand/><p role="status">Opening PalmPay…</p></main>}><Routes>
  <Route path="/wallet/*" element={<Wallet/>}/><Route path="/merchant/*" element={<Merchant/>}/><Route path="*" element={<Landing/>}/>
</Routes></Suspense></BrowserRouter></QueryClientProvider></React.StrictMode>)

