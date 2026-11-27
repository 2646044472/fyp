import { assign, createMachine } from 'xstate'
import type { Payment } from '../../../packages/shared-types'
export const paymentMachine = createMachine({
  types: {} as { context: { payment: Payment | null }; events: { type: 'SYNC'; payment: Payment } | { type: 'RESET' } },
  initial: 'checkout',
  context: {payment:null},
  on: {
    RESET: {target:'.checkout', actions:assign({payment:null})},
    SYNC: [
      {guard:({event})=>event.payment.status==='paid',target:'.paid',actions:assign({payment:({event})=>event.payment})},
      {guard:({event})=>['failed','expired','cancelled'].includes(event.payment.status),target:'.closed',actions:assign({payment:({event})=>event.payment})},
      {target:'.waiting',actions:assign({payment:({event})=>event.payment})}
    ]
  },
  states:{checkout:{},waiting:{},paid:{},closed:{}}
})

