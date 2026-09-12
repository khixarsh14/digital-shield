import assert from 'node:assert/strict'
import { createServer } from 'vite'

const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' })
const originalFetch = globalThis.fetch
try {
  const { verifyContent } = await server.ssrLoadModule('/src/services/api.js')
  for (const [content, expected] of [
    ['Please send your OTP now.', 'red'],
    ['See you at the library tomorrow.', 'green'],
    ['http://example.com', 'yellow'],
    ['https://example.com', 'green'],
  ]) {
    const result = await verifyContent(content)
    assert.equal(result.status, expected)
    assert.equal(result.language, 'en')
    console.log(`PASS live verification: ${expected} (${content})`)
  }
  for (const origin of ['http://localhost:5173', 'http://127.0.0.1:5173']) {
    const response = await originalFetch(`${process.env.VITE_API_URL}/verify`, {
      method: 'OPTIONS',
      headers: { Origin: origin, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type' },
    })
    assert.equal(response.headers.get('access-control-allow-origin'), origin)
  }
  console.log('PASS both development CORS origins')
  for (const failure of [
    async () => { throw new TypeError('private network details') },
    async () => new Response('private exception', { status: 500 }),
    async () => new Response('not json'),
    async () => Response.json({ status: 'unknown' }),
  ]) {
    globalThis.fetch = failure
    await assert.rejects(verifyContent('example'), { message: "We couldn't verify this content right now. Please try again." })
  }
  console.log('PASS network, HTTP, JSON, and schema failures use friendly errors')
  let finish
  globalThis.fetch = () => new Promise((resolve) => { finish = resolve })
  let settled = false
  const pending = verifyContent('example').then(() => { settled = true })
  await new Promise((resolve) => setTimeout(resolve, 50))
  assert.equal(settled, false)
  finish(Response.json({ status: 'green', label: 'Backend label', summary: 'Backend summary', reasons: [], actions: [], sources: [], needs_followup: false, followup_question: null, language: 'en' }))
  await pending
  console.log('PASS service remains pending until response arrives')
} finally {
  globalThis.fetch = originalFetch
  await server.close()
}
