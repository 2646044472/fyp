import { createActor } from 'xstate'
import { expect, test } from 'vitest'
import type { Payment } from '../../../packages/shared-types'
import { paymentMachine } from './payment'

test('the POS reflects the server state and clears on a new order', () => {
  const actor = createActor(paymentMachine).start()
  const base: Payment = { id:'one', order_id:'order', merchant:'CKLC Coffee', amount:2500, currency:'MOP', status:'awaiting_authorization', reason:null, expires_at:100, reference:null, paid_at:null, items:[] }
  for (const [status, state] of [['awaiting_authorization','waiting'],['expired','closed'],['awaiting_authorization','waiting'],['paid','paid']]) {
    actor.send({type:'SYNC',payment:{...base,status}})
    expect(actor.getSnapshot().value).toBe(state)
  }
  actor.send({type:'RESET'})
  expect(actor.getSnapshot().context.payment).toBeNull()
  expect(actor.getSnapshot().value).toBe('checkout')
  actor.stop()
})

