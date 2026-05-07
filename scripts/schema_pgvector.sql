-- Claude Memory Skill — Semantic Search (Future)
--
-- This file is a draft for a future semantic search implementation
-- using pgvector (https://github.com/pgvector/pgvector) and Supabase's
-- built-in pgvector support.
--
-- Current state: the production schema (schema.sql) uses TSVECTOR-based
-- full-text keyword search. This covers the primary use case effectively.
--
-- Semantic search (finding memories by meaning even when keywords don't
-- match exactly) is planned for a future release. It will use embedding
-- models to generate vectors for each memory summary and store them in
-- a pgvector column, enabling cosine similarity search.
--
-- Track progress: https://github.com/ShibanBanerjee/claude-memory-skill/issues

-- Enable pgvector (already available on Supabase)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Draft: add a vector column to claude_memories
-- ALTER TABLE claude_memories ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Draft: index for approximate nearest-neighbor search
-- CREATE INDEX IF NOT EXISTS claude_memories_embedding_idx
--     ON claude_memories USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

-- Draft: semantic search query
-- SELECT id, title, project, updated_at,
--        1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
-- FROM claude_memories
-- ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
-- LIMIT 5;
