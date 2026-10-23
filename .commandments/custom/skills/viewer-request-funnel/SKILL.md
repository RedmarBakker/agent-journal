---
name: ViewerRequestFunnel
description: Load it before the viewer asks the server for anything, or before writing a poll, so every request goes through the one transport and every poll through the static poll table.
summary: Only src/web/src/api/transport.js calls fetch; a read is declared once in the API client under a key, one request per key is in flight, and a poll is an entry of the static poll table whose data is read from it.
tier: mandatory
languages: [typescript]
---

# The viewer's request funnel

The viewer reaches the journal server through one funnel: the transport, `src/web/src/api/transport.js`. It is the
only code that calls `fetch`, opens an `EventSource` or an `XMLHttpRequest`, or sends a beacon. Everything else asks
the API client (`src/web/src/api/client.js`), which declares every read and write once.

Every read has a key that names what it reads, never its query: `messages.page`, `messages.older`,
`messages.changes`. A `since`, a `before` or a `limit` never makes a second key. One request per key is in flight: a
read for a key already in flight is not sent, and its caller takes the answer of the one in flight. So a burst of
refreshes is one request, and a slow answer can never pile up a queue behind it.

A file the build carries beside the page (a figure's model, its wardrobe) is read with `transport.file(url)`, which
holds it to the same rule.

## Fix

Move the request into the client as a declared read or write, and call that. A file the build carries goes through
`transport.file`. Never call `fetch` beside the transport, not even for a "quick" check.
