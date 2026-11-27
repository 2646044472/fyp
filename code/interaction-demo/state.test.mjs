import test from 'node:test';
import assert from 'node:assert/strict';
import { createState, transition } from './state.mjs';

test('verification locks its result until removal and supports a new attempt', () => {
  let state = transition(createState(), 'start');
  state = transition(state, 'place');
  state = transition(state, 'result', { outcome: 'match' });
  assert.equal(state.phase, 'result');
  assert.equal(transition(state, 'place').phase, 'result');
  state = transition(state, 'remove');
  assert.equal(state.phase, 'waiting');
  assert.equal(state.outcome, null);
});

test('stop, navigation and camera failure invalidate processing', () => {
  const state = transition(transition(createState(), 'start'), 'place');
  for (const event of ['stop', 'error', 'enroll']) {
    const next = transition(state, event);
    assert.notEqual(next.phase, 'processing');
    assert.notEqual(transition(next, 'result', { outcome: 'match' }).phase, 'result');
  }
});

test('enrollment preserves the five-second preview and sixty-second active minimum', () => {
  let state = transition(transition(createState(), 'enroll'), 'start');
  state = transition(state, 'tick', { seconds: 4 });
  assert.equal(state.phase, 'preview');
  state = transition(state, 'tick', { seconds: 1 });
  assert.equal(state.phase, 'capturing');
  state = transition(state, 'tick', { seconds: 59 });
  assert.equal(state.phase, 'capturing');
  state = transition(state, 'pause');
  assert.equal(transition(state, 'tick', { seconds: 100 }).elapsed, 59);
  state = transition(state, 'resume');
  state = transition(state, 'tick', { seconds: 1 });
  assert.equal(state.phase, 'review');
  assert.equal(state.photos.length, 10);
});

test('confirmation requires ten groups and explicit consent', () => {
  let state = { ...createState(), mode: 'enroll', phase: 'review', photos: Array.from({length:10}, (_, index) => index + 1) };
  assert.equal(transition(state, 'save').phase, 'review');
  state = transition(state, 'delete', { id: 3 });
  state = transition(state, 'consent', { value: true });
  assert.equal(transition(state, 'save').phase, 'review');
  state = transition(state, 'replace');
  assert.equal(state.consent, false);
  state = transition(state, 'consent', { value: true });
  assert.equal(transition(state, 'save').phase, 'saved');
});
