-- RAG System Database Schema for Supabase with pgvector
-- Run this SQL to set up the necessary tables and indexes

-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Table to store document metadata and content
CREATE TABLE documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('pdf', 'txt')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    file_size INTEGER,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_date TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'error')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table to store document chunks with embeddings
CREATE TABLE document_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding vector(1536), -- OpenAI ada-002 produces 1536-dimensional vectors
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique chunk ordering within each document
    UNIQUE(document_id, chunk_index)
);

-- Table to store search queries and their results for analytics
CREATE TABLE search_queries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    response_text TEXT,
    source_document_ids UUID[],
    response_time_ms INTEGER,
    relevance_score FLOAT,
    user_feedback INTEGER CHECK (user_feedback BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for optimal performance

-- Index for document lookups
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_upload_date ON documents(upload_date DESC);
CREATE INDEX idx_documents_file_type ON documents(file_type);

-- Vector similarity search index (HNSW for best performance)
CREATE INDEX idx_document_chunks_embedding ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index for chunk retrieval by document
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_token_count ON document_chunks(token_count);

-- Index for search analytics
CREATE INDEX idx_search_queries_created_at ON search_queries(created_at DESC);
CREATE INDEX idx_search_queries_response_time ON search_queries(response_time_ms);

-- Function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

-- Triggers to automatically update timestamps
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_chunks_updated_at 
    BEFORE UPDATE ON document_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for vector similarity search with metadata filtering
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_document_ids uuid[] DEFAULT NULL
)
RETURNS TABLE (
    chunk_id uuid,
    document_id uuid,
    filename text,
    content text,
    similarity float,
    chunk_index int,
    token_count int,
    metadata jsonb
) 
LANGUAGE plpgsql
AS $
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        d.filename,
        dc.content,
        (dc.embedding <=> query_embedding) as similarity,
        dc.chunk_index,
        dc.token_count,
        dc.metadata
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 
        (dc.embedding <=> query_embedding) > similarity_threshold
        AND (filter_document_ids IS NULL OR d.id = ANY(filter_document_ids))
        AND d.status = 'completed'
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$;

-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents bigint,
    completed_documents bigint,
    total_chunks bigint,
    avg_chunks_per_document float,
    total_tokens bigint,
    avg_tokens_per_chunk float
)
LANGUAGE plpgsql
AS $
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(d.id) as total_documents,
        COUNT(CASE WHEN d.status = 'completed' THEN 1 END) as completed_documents,
        COUNT(dc.id) as total_chunks,
        CASE 
            WHEN COUNT(d.id) > 0 THEN COUNT(dc.id)::float / COUNT(d.id)::float 
            ELSE 0 
        END as avg_chunks_per_document,
        COALESCE(SUM(dc.token_count), 0) as total_tokens,
        CASE 
            WHEN COUNT(dc.id) > 0 THEN AVG(dc.token_count)
            ELSE 0 
        END as avg_tokens_per_chunk
    FROM documents d
    LEFT JOIN document_chunks dc ON d.id = dc.document_id;
END;
$;

-- Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations for authenticated users
-- Adjust these policies based on your authentication requirements
CREATE POLICY "Allow all operations for authenticated users" ON documents
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON document_chunks
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON search_queries
    FOR ALL USING (auth.role() = 'authenticated');

-- Grant permissions to authenticated role
GRANT ALL ON documents TO authenticated;
GRANT ALL ON document_chunks TO authenticated;
GRANT ALL ON search_queries TO authenticated;
GRANT EXECUTE ON FUNCTION search_similar_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION get_document_stats TO authenticated;

-- Insert sample data for testing (optional)
INSERT INTO documents (filename, file_type, content, status) VALUES 
('sample.txt', 'txt', 'This is a sample document for testing the RAG system. It contains information about artificial intelligence and machine learning.', 'completed');

-- Get the document ID for the sample chunk
DO $
DECLARE
    doc_id uuid;
BEGIN
    SELECT id INTO doc_id FROM documents WHERE filename = 'sample.txt';
    
    INSERT INTO document_chunks (document_id, chunk_index, content, token_count) VALUES 
    (doc_id, 0, 'This is a sample document for testing the RAG system.', 12),
    (doc_id, 1, 'It contains information about artificial intelligence and machine learning.', 10);
END $;

-- Verify the setup
SELECT 'Setup completed successfully!' as status;
SELECT * FROM get_document_stats();