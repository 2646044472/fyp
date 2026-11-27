import { Check, ReceiptText } from 'lucide-react'
import { money, stamp } from './index'
import type { Payment } from '../shared-types'
export function Receipt({ payment }: { payment: Payment }) {
  return <section className="receipt">
    <span className="status-icon"><Check /></span>
    <h2>{payment.merchant}</h2><p>{payment.paid_at && stamp(payment.paid_at)}</p>
    <strong className="receipt-value">MOP {money(payment.amount)}</strong>
    <div className="receipt-lines">{payment.items.map(item => <div className="row" key={item.product_id}><span>{item.quantity} × {item.name}</span><b>{money(item.price*item.quantity)}</b></div>)}</div>
    <div className="receipt-reference"><ReceiptText size={16}/> {payment.reference}</div>
  </section>
}

