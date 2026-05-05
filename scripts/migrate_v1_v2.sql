-- Migration: v1 to v2
-- Adds: instructions column, updated_at column, RLS policy update

ALTER TABLE claude_memories
  ADD COLUMN IF NOT EXISTS instructions JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- Update trigger to set updated_at
CREATE OR REPLACE FUNCTION claude_memories_search_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := to_tsvector('english',
    COALESCE(NEW.title, '')   || ' ' ||
    COALESCE(NEW.project, '') || ' ' ||
    COALESCE(NEW.summary, '') || ' ' ||
    COALESCE(array_to_string(NEW.tags, ' '), '')
  );
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
