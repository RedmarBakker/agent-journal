---
name: page-sizes-read
description: A page size handed to a function bounds its read; load it when unused-page-size fires
---

# Page sizes are read

A function that takes `limit`, `page`, `page_size`, `count` or a `listing` promises its caller a bounded read.
If the body never reads that parameter, the read takes every row while the caller believes it took a page:
the chat's catch-up read once ignored its listing's limit and pulled 500 messages into the tab.

## What to do

- Pass the size on to the query: `self.selected(query.order_descending("id").limit(limit))`.
- If the read is meant to be whole, remove the parameter and the argument every caller passes, and call the
  repository's whole read by name, so the record of large reads (`journal developer reads`) shows it.
- Never keep the parameter "for later": a size nobody reads is a bound nobody keeps.
