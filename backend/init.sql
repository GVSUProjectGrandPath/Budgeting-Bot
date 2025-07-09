-- Initialize pgpfinlitbot database with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom functions for vector operations
CREATE OR REPLACE FUNCTION cosine_similarity(a vector, b vector)
RETURNS float
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN 1 - (a <=> b);
END;
$$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
ON messages(timestamp);

CREATE INDEX IF NOT EXISTS idx_vectors_source_type 
ON vectors(source_type);

-- Create vector index for similarity search
CREATE INDEX IF NOT EXISTS idx_vectors_embedding 
ON vectors USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pgpbot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pgpbot;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO pgpbot; 