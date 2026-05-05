-- Claude Memory System — Schema
-- Run this once in your Supabase SQL editor before using the /mem skill

-- Enable full-text search (already available in Postgres, no extension needed)
-- Enable pgvector for future semantic search (optional)
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS claude_memories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  conversation_id TEXT,
  conversation_url TEXT,
  title           TEXT NOT NULL,
  project         TEXT,
  summary         TEXT NOT NULL,
  key_decisions   JSONB DEFAULT '[]'::jsonb,
  open_questions  JSONB DEFAULT '[]'::jsonb,
  entities        JSONB DEFAULT '{}'::jsonb,
  tags            TEXT[] DEFAULT '{}',
  token_count_est INTEGER,
  -- Full-text search vector (auto-generated)
  search_vector   TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('english',
      COALESCE(title, '') || ' ' ||
      COALESCE(project, '') || ' ' ||
      COALESCE(summary, '') || ' ' ||
      COALESCE(array_to_string(tags, ' '), '')
    )
  ) STORED
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_memories_search   ON claude_memories USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_memories_tags     ON claude_memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_project  ON claude_memories (project);
CREATE INDEX IF NOT EXISTS idx_memories_created  ON claude_memories (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_conv_id  ON claude_memories (conversation_id);

-- RLS: disable for personal use, or enable and add policies for team use
ALTER TABLE claude_memories DISABLE ROW LEVEL SECURITY;

-- Useful view: memory cards (compact, for quick listing)
CREATE OR REPLACE VIEW memory_cards AS
SELECT
  id,
  created_at::DATE                    AS date,
  title,
  project,
  tags,
  LEFT(summary, 200) || '...'         AS preview,
  jsonb_array_length(key_decisions)   AS decision_count,
  jsonb_array_length(open_questions)  AS question_count,
  conversation_url
FROM claude_memories
ORDER BY created_at DESC;
