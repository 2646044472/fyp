import { Hand, X } from 'lucide-react'
import { useEffect, useRef, type ReactNode } from 'react'
export function Brand({ merchant = false }: { merchant?: boolean }) {
  return <div className="brand"><span className="brand-mark"><Hand size={19}/></span><strong>palmpay<span>.</span></strong>{merchant && <small>MERCHANT</small>}</div>
}
export function Dialog({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => { ref.current?.showModal() }, [])
  return <dialog ref={ref} onCancel={event => {event.preventDefault(); onClose()}} aria-label={title}>
    <div className="row"><h2>{title}</h2><button className="icon-button" aria-label="Close" onClick={onClose}><X size={20}/></button></div>{children}
  </dialog>
}
export const money = (minor: number) => (minor / 100).toLocaleString('en-MO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export const stamp = (time: string) => new Intl.DateTimeFormat('en-MO', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Macau' }).format(new Date(time))

