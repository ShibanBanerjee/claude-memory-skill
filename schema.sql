-- Claude Memory Skill — PostgreSQL Schema
-- Run this once in your Supabase SQL Editor to set up the memory table.
-- Navigate to: Supabase Dashboard → SQL Editor → New Query → paste and run.

-- ── Main table ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS claude_memories (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title            TEXT NOT NULL,
    project          TEXT NOT NULL DEFAULT '',
    conversation_url TEXT NOT NULL DEFAULT '',
    summary          TEXT NOT NULL,
    key_decisions    JSONB NOT NULL DEFAULT '[]',
    open_questions   JSONB NOT NULL DEFAULT '[]',
    entities         JSONB NOT NULL DEFAULT '{}',
    tags             TEXT[] NOT NULL DEFAULT '{}',
    token_count_est  INTEGER NOT NULL DEFAULT 0,
    search_vector    TSVECTOR
);

-- ── Indexes ───────────────────────────────────────────────────────────────────

-- Full-text search index
CREATE INDEX IF NOT EXISTS claude_memories_fts_idx
    ON claude_memories USING GIN (search_vector);

-- Tag array lookups
CREATE INDEX IF NOT EXISTS claude_memories_tags_idx
    ON claude_memories USING GIN (tags);

-- Project + recency queries
CREATE INDEX IF NOT EXISTS claude_memories_project_updated_idx
    ON claude_memories (project, updated_at DESC);

-- ── Full-text search trigger ──────────────────────────────────────────────────

-- Trigger function: populate search_vector from title, project, summary, and tags
CREATE OR REPLACE FUNCTION claude_memories_search_vector_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.search_vector :=
        to_tsvector('english',
            coalesce(NEW.title, '') || ' ' ||
            coalesce(NEW.project, '') || ' ' ||
            coalesce(NEW.summary, '') || ' ' ||
            coalesce(array_to_string(NEW.tags, ' '), '')
        );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS claude_memories_search_vector_trigger ON claude_memories;
CREATE TRIGGER claude_memories_search_vector_trigger
    BEFORE INSERT OR UPDATE ON claude_memories
    FOR EACH ROW EXECUTE FUNCTION claude_memories_search_vector_update();

-- ── Access control ────────────────────────────────────────────────────────────

-- Disable Row Level Security so the anon key can read and write freely.
-- To restrict access to specific users, enable RLS and add policies here.
ALTER TABLE claude_memories DISABLE ROW LEVEL SECURITY;
