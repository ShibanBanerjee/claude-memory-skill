-- Claude Memory Skill — pgvector Extension (Optional)
-- Enables semantic/meaning-based search in addition to keyword search.
-- Run AFTER schema.sql. Requires Supabase Pro or pgvector extension enabled.

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE claude_memories
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_memories_embedding
ON claude_memories USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Semantic search function
CREATE OR REPLACE FUNCTION search_memories_semantic(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  title text,
  project text,
  summary text,
  tags text[],
  similarity float
)
LANGUAGE sql STABLE AS $$
  SELECT
    id, title, project, summary, tags,
    1 - (embedding <=> query_embedding) AS similarity
  FROM claude_memories
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
