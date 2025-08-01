-- Mayan EDMS - Fix auth_user sequence after manual database manipulation
-- Run this script in the PostgreSQL Docker container to fix the sequence issue

-- First, let's see the current state
SELECT 'Current users in auth_user table:' as info;
SELECT id, username, email FROM auth_user ORDER BY id;

SELECT 'Current sequence state:' as info;
SELECT last_value, is_called FROM auth_user_id_seq;

-- Get the maximum ID
SELECT 'Maximum user ID:' as info, MAX(id) as max_id FROM auth_user;

-- Fix the sequence by setting it to max_id + 1
-- This will make the next user start from the correct ID
SELECT setval('auth_user_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM auth_user));

-- Verify the fix
SELECT 'Sequence fixed. New sequence value:' as info;
SELECT last_value FROM auth_user_id_seq;

-- Show final state
SELECT 'Final user list:' as info;
SELECT id, username, email FROM auth_user ORDER BY id; 