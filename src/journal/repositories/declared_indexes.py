from journal.db.index import Index
from journal.db.partial_index import PartialIndex
from journal.repositories.entries import DISPATCHES

INDEXES = (
    Index("agents_by_session", "agents", "session"),
    Index("agents_by_state", "agents", "environment_id, state"),
    Index("edits_by_session", "edits", "environment_id, session, time"),
    Index("entries_by_actor", "entries", "actor, id"),
    Index("entries_by_environment", "entries", "environment_id, id"),
    Index("entries_by_kind_id", "entries", "environment_id, kind, id"),
    PartialIndex("entries_dispatches", "entries", "environment_id, id", condition=DISPATCHES.clause()),
    Index("environments_key", "environments", "key", unique=True),
    Index("links_by_kind", "links", "kind, source"),
    Index("links_by_source", "links", "source"),
    Index("links_by_target", "links", "target"),
    Index("messages_by_chat", "messages", "environment_id, agent_role, id"),
    Index("messages_by_environment", "messages", "environment_id, id"),
    Index("messages_by_key", "messages", "environment_id, idempotency"),
    Index("messages_by_reply", "messages", "reply_target"),
    Index("messages_by_session", "messages", "session, id"),
    Index("messages_by_update", "messages", "environment_id, updated_at"),
    Index("messages_by_writer", "messages", "environment_id, creator"),
    Index("messages_unread", "messages", "environment_id, author, read_at"),
    Index("outputs_by_chain", "command_outputs", "chain, id"),
    Index("statistics_by_key", "statistics", "key"),
    Index("tasks_by_state", "tasks", "environment_id, state, id"),
)

