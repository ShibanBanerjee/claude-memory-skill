-- Claude Memory Skill — Database Schema v1.2
-- Run this once in your Supabase SQL Editor before using the skill.

-- Table
CREATE TABLE IF NOT EXISTS claude_memories (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ,
  conversation_id  TEXT,
  conversation_url TEXT,
  title            TEXT NOT NULL,
  project          TEXT,
  summary          TEXT NOT NULL,
  key_decisions    JSONB DEFAULT '[]'::jsonb,
  open_questions   JSONB DEFAULT '[]'::jsonb,
  instructions     JSONB DEFAULT '[]'::jsonb,
  entities         JSONB DEFAULT '{}'::jsonb,
  tags             TEXT[] DEFAULT '{}',
  token_count_est  INTEGER,
  search_vector    TSVECTOR
);

-- Auto-update search vector on insert/update
CREATE OR REPLACE FUNCTION claude_memories_search_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := to_tsvector('english',
    COALESCE(NEW.title, '')    || ' ' ||
    COALESCE(NEW.project, '')  || ' ' ||
    COALESCE(NEW.summary, '')  || ' ' ||
    COALESCE(array_to_string(NEW.tags, ' '), '')
  );
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER claude_memories_search_trigger
BEFORE INSERT OR UPDATE ON claude_memories
FOR EACH ROW EXECUTE FUNCTION claude_memories_search_update();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_memories_search   ON claude_memories USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_memories_tags     ON claude_memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_project  ON claude_memories (project);
CREATE INDEX IF NOT EXISTS idx_memories_created  ON claude_memories (created_at DESC);

-- RLS: enable with open policy for personal use
ALTER TABLE claude_memories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_personal_use" ON claude_memories FOR ALL USING (true) WITH CHECK (true);

-- Convenience view
CREATE OR REPLACE VIEW memory_cards AS
SELECT
  id,
  created_at::DATE                    AS date,
  updated_at::DATE                    AS last_updated,
  title,
  project,
  tags,
  LEFT(summary, 300) || '...'         AS preview,
  jsonb_array_length(key_decisions)   AS decision_count,
  jsonb_array_length(open_questions)  AS question_count,
  jsonb_array_length(instructions)    AS instruction_count,
  token_count_est,
  conversation_url
FROM claude_memories
ORDER BY created_at DESC;
