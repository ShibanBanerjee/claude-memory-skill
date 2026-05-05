-- Claude Memory Skill — SQLite Schema
-- Applied automatically by mem.py on first run.
-- This file is provided as a reference. You do not need to run it manually.

PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS claude_memories (
    id               TEXT PRIMARY KEY,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    title            TEXT NOT NULL,
    project          TEXT NOT NULL DEFAULT '',
    conversation_url TEXT NOT NULL DEFAULT '',
    summary          TEXT NOT NULL,
    key_decisions    TEXT NOT NULL DEFAULT '[]',
    open_questions   TEXT NOT NULL DEFAULT '[]',
    entities         TEXT NOT NULL DEFAULT '{}',
    tags             TEXT NOT NULL DEFAULT '[]',
    token_count_est  INTEGER NOT NULL DEFAULT 0
);

-- Full-text search index across title, project, summary, and tags
CREATE VIRTUAL TABLE IF NOT EXISTS claude_memories_fts
USING fts5(
    title, project, summary, tags,
    content='claude_memories',
    content_rowid='rowid'
);

-- Keep FTS in sync on insert
CREATE TRIGGER IF NOT EXISTS memories_ai
AFTER INSERT ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(rowid, title, project, summary, tags)
    VALUES (new.rowid, new.title, new.project, new.summary, new.tags);
END;

-- Keep FTS in sync on update
CREATE TRIGGER IF NOT EXISTS memories_au
AFTER UPDATE ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(claude_memories_fts, rowid, title, project, summary, tags)
    VALUES ('delete', old.rowid, old.title, old.project, old.summary, old.tags);
    INSERT INTO claude_memories_fts(rowid, title, project, summary, tags)
    VALUES (new.rowid, new.title, new.project, new.summary, new.tags);
END;

-- Keep FTS in sync on delete
CREATE TRIGGER IF NOT EXISTS memories_ad
AFTER DELETE ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(claude_memories_fts, rowid, title, project, summary, tags)
    VALUES ('delete', old.rowid, old.title, old.project, old.summary, old.tags);
END;
