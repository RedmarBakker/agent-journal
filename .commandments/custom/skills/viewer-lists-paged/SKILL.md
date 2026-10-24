---
name: ViewerListsPaged
description: Load it before the viewer lists a table's rows, so every list request is paged.
summary: A viewer list call names its limit or the ids it holds; nothing reads a whole table.
tier: mandatory
languages: [typescript, vue]
---

# Viewer lists are paged

A list request with no limit makes the server read and send every row of its table, on every poll. A table grows
for as long as the project lives, so the request grows with it.

## The rule

- Every `api.list(table, ...)` names its `limit`: `pageOf(table)` from `sync/paging.js`, or a smaller number when
  fewer are wanted (one row, to know whether any exist).
- A call that holds rows already asks for them by `ids`.
- Older rows load a page at a time with `before`, never by raising the limit.

## Example

Bad: `api.list("plugins")`

Good: `api.list("plugins", {limit: pageOf("plugins")})`
