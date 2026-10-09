// Demo mode only: show the last email the core API generated locally.
export async function GET() {
  if (process.env.NEXT_PUBLIC_DEMO_MODE !== 'true') {
    return new Response('Not found', { status: 404 });
  }
  const api = process.env.NIYOZ_DEV_API_URL || 'http://127.0.0.1:8000';
  const res = await fetch(`${api}/demo/outbox/latest`, { cache: 'no-store' });
  return new Response(await res.text(), {
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
}
