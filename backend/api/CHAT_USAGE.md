# Chat WebSocket Usage (MVP)

Example: connect and start a session

JavaScript example (browser):

```js
const ws = new WebSocket("ws://localhost:8000/ws/chat");
ws.addEventListener('open', () => {
  // initialize a session with optional context
  ws.send(JSON.stringify({type: 'init', context: { transliteration: { explanation: 'Example explanation' }}}));
});

ws.addEventListener('message', (ev) => {
  const data = JSON.parse(ev.data);
  console.log('incoming', data);
  if (data.type === 'session') {
    const sessionId = data.session_id;
    // send a user message
    ws.send(JSON.stringify({type: 'user', session_id: sessionId, text: 'Can you explain the transliteration?'}));
  }
});
```

Server messages:
- `{ type: 'session', session_id }` — session created
- `{ type: 'assistant', text, partial, session_id }` — streaming assistant chunks. `partial` is true until final chunk.

Notes:
- Sessions are stored in-memory (MVP). For production, add persistence and authentication.
- The `transliterate` endpoint now returns `session_id` when run via the API so you can follow-up on transliterations directly in chat.
