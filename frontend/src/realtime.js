import { useEffect, useRef, useState } from 'react';

// fetch streaming retains the JWT in the Authorization header, never in a URL.
export function useRealtime(token, onEvent, onUnauthorized) {
  const [status, setStatus] = useState('connecting');
  const eventRef = useRef(onEvent), unauthorizedRef = useRef(onUnauthorized);
  eventRef.current = onEvent; unauthorizedRef.current = onUnauthorized;
  useEffect(() => {
    if (!token) return;
    let disposed = false, controller, retryTimer, watchdog;
    let retry = 1000;
    async function connect() {
      controller = new AbortController();
      setStatus('connecting');
      let lastBeat = Date.now();
      watchdog = window.setInterval(() => { if (Date.now() - lastBeat > 45000) controller.abort(); }, 10000);
      try {
        const response = await fetch('/api/events', { headers: { Authorization: `Bearer ${token}`, Accept: 'text/event-stream' }, signal: controller.signal, cache: 'no-store' });
        if (response.status === 401) { unauthorizedRef.current(); return; }
        if (!response.ok || !response.body) throw new Error('Stream unavailable');
        const reader = response.body.getReader(), decoder = new TextDecoder();
        let buffer = '';
        while (!disposed) {
          const { value, done } = await reader.read();
          if (done) break;
          lastBeat = Date.now();
          buffer += decoder.decode(value, { stream: true });
          buffer = buffer.replace(/\r\n/g, '\n');
          let end;
          while ((end = buffer.indexOf('\n\n')) !== -1) {
            const block = buffer.slice(0, end); buffer = buffer.slice(end + 2);
            const data = block.split('\n').filter(line => line.startsWith('data:')).map(line => line.slice(5).trimStart()).join('\n');
            if (!data) continue;
            const event = JSON.parse(data);
            if (event.type === 'session.expired') { unauthorizedRef.current(); controller.abort(); return; }
            if (event.type === 'unavailable') throw new Error('Stream unavailable');
            if (event.type === 'ready') { retry = 1000; setStatus('live'); }
            eventRef.current(event);
          }
        }
      } catch { /* Connection state and retry tell the user how to recover. */ }
      finally { window.clearInterval(watchdog); controller.abort(); }
      if (!disposed) {
        setStatus('reconnecting');
        retryTimer = window.setTimeout(connect, retry);
        retry = Math.min(retry * 2, 15000);
      }
    }
    const offline = () => controller?.abort();
    window.addEventListener('offline', offline);
    connect();
    return () => { disposed = true; controller?.abort(); window.clearTimeout(retryTimer); window.clearInterval(watchdog); window.removeEventListener('offline', offline); };
  }, [token]);
  return status;
}
