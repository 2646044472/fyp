export class ApiError extends Error {
  constructor(readonly status: number, message: string) { super(message) }
}
export async function api<T = unknown>(path: string, method = 'GET', body?: unknown, key?: string): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (key) headers['Idempotency-Key'] = key
  const response = await fetch('/api'+path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) })
  if (!response.ok) {
    const problem = await response.json().catch(() => ({}))
    throw new ApiError(response.status, typeof problem.detail === 'string' ? problem.detail : 'Check your details and try again.')
  }
  return response.json()
}
export const requestKey = () => Array.from(crypto.getRandomValues(new Uint8Array(16)), byte => byte.toString(16).padStart(2,'0')).join('')

