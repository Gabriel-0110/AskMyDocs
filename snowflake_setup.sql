-- Snowflake Streamlit Secrets Setup
-- Execute these commands in your Snowflake SQL worksheet
-- IMPORTANT: Replace the placeholder values with your actual API keys

-- 1. First, ensure you're using the correct database
USE DATABASE APPS;

-- 2. Create the secrets for your RAG system
CREATE SECRET IF NOT EXISTS anthropic_api_key
TYPE = PASSWORD
USERNAME = 'api_key'
PASSWORD = 'your_anthropic_api_key_here';

CREATE SECRET IF NOT EXISTS supabase_url
TYPE = PASSWORD
USERNAME = 'url'
PASSWORD = 'your_supabase_project_url_here';

CREATE SECRET IF NOT EXISTS supabase_anon_key
TYPE = PASSWORD
USERNAME = 'api_key'
PASSWORD = 'your_supabase_anon_key_here';

CREATE SECRET IF NOT EXISTS openai_api_key
TYPE = PASSWORD
USERNAME = 'api_key'
PASSWORD = 'your_openai_api_key_here';

-- 3. Verify the secrets were created
SHOW SECRETS;

-- 4. Grant access to the secrets (adjust role as needed)
GRANT USAGE ON SECRET anthropic_api_key TO ROLE PUBLIC;
GRANT USAGE ON SECRET supabase_url TO ROLE PUBLIC;
GRANT USAGE ON SECRET supabase_anon_key TO ROLE PUBLIC;
GRANT USAGE ON SECRET openai_api_key TO ROLE PUBLIC;
