-- =============================================================
-- Row Level Security (RLS) & Serverless Storage Migration
-- Execute this script in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/aihknstwsdkvsviomztk/sql
-- =============================================================

-- 1. Enable Row Level Security (RLS) across all 10 tables
-- This ensures anonymous/public API clients cannot read or modify any tables directly.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE hits ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE passcodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE media ENABLE ROW LEVEL SECURITY;

-- 2. Add content_b64 column to media table for persistent serverless file storage
ALTER TABLE media ADD COLUMN IF NOT EXISTS content_b64 TEXT DEFAULT '';

-- NOTE: Your backend on Vercel connects with the postgres user (or service_role key),
-- which automatically bypasses RLS so your Flask backend retains full management control.

