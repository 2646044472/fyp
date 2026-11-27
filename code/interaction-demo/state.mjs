export function createState(mode = 'verify') {
  return { mode, phase: 'idle', elapsed: 0, preview: 0, photos: [], consent: false, outcome: null, resumePhase: null };
}

export function transition(state, event, data = {}) {
  if (event === 'verify' || event === 'enroll') return createState(event);
  if (event === 'stop') return createState(state.mode);
  if (event === 'error') return { ...state, phase: 'error', outcome: null };
  if (event === 'start' || event === 'retry') {
    if (!['idle', 'error', 'saved'].includes(state.phase)) return state;
    return { ...createState(state.mode), phase: state.mode === 'verify' ? 'waiting' : 'preview' };
  }
  if (state.mode === 'verify') {
    if (event === 'place' && state.phase === 'waiting') return { ...state, phase: 'processing' };
    if (event === 'result' && state.phase === 'processing') return { ...state, phase: 'result', outcome: data.outcome };
    if (event === 'remove' && ['processing', 'result'].includes(state.phase)) return { ...state, phase: 'waiting', outcome: null };
    return state;
  }
  if (event === 'pause' && ['preview', 'capturing'].includes(state.phase)) return { ...state, resumePhase: state.phase, phase: 'paused' };
  if (event === 'resume' && state.phase === 'paused') return { ...state, phase: state.resumePhase, resumePhase: null };
  if (event === 'tick' && state.phase === 'preview') {
    const preview = Math.min(5, state.preview + data.seconds);
    return { ...state, preview, phase: preview >= 5 ? 'capturing' : 'preview' };
  }
  if (event === 'tick' && state.phase === 'capturing') {
    const elapsed = Math.min(60, state.elapsed + data.seconds);
    const count = Math.min(10, Math.floor(elapsed / 6));
    return { ...state, elapsed, photos: Array.from({ length: count }, (_, index) => index + 1), phase: elapsed >= 60 ? 'review' : 'capturing' };
  }
  if (state.phase !== 'review') return state;
  if (event === 'delete') return { ...state, photos: state.photos.filter(id => id !== data.id), consent: false };
  if (event === 'replace') {
    const used = new Set(state.photos);
    const replacements = Array.from({length:10}, (_, index) => index + 1).filter(id => !used.has(id));
    return { ...state, photos: [...state.photos, ...replacements].sort((a,b) => a-b), consent: false };
  }
  if (event === 'consent') return { ...state, consent: Boolean(data.value) };
  if (event === 'save' && state.photos.length === 10 && state.consent) return { ...state, phase: 'saved' };
  return state;
}
