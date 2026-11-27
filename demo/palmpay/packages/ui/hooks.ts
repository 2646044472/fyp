import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
export function useEvents(role: 'wallet' | 'merchant', enabled: boolean) {
  const queryClient = useQueryClient()
  useEffect(() => {
    if (!enabled) return
    let socket: WebSocket | undefined
    let timer: number | undefined
    let stopped = false
    const refresh = () => { void queryClient.invalidateQueries({ queryKey: [role] }) }
    function connect() {
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      socket = new WebSocket(protocol+'//'+location.host+'/ws/events?role='+role)
      socket.onopen = refresh
      socket.onmessage = refresh
      socket.onclose = () => { if (!stopped) timer = window.setTimeout(connect, 1600) }
    }
    connect()
    window.addEventListener('online', refresh)
    return () => {
      stopped = true
      window.clearTimeout(timer)
      socket?.close()
      window.removeEventListener('online', refresh)
    }
  }, [enabled, queryClient, role])
}

