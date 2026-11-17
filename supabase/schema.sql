-- Supabase schema for the cloud video pipeline.
-- Run this once in: Supabase Dashboard -> SQL Editor -> New query -> Run.

-- 1. Job log: one row per pipeline run
create table if not exists public.jobs (
  id bigint generated always as identity primary key,
  topic text not null,
  status text not null default 'running',   -- running | done | failed
  rating int,                                -- reviewer score 1-10
  storage_object text,                       -- object name in the `videos` bucket
  error text,
  created_at timestamptz not null default now()
);

-- 2. Topic rotation state (survives ephemeral CI runners)
create table if not exists public.topic_state (
  id int primary key,
  index int not null default 0,
  updated_at timestamptz not null default now()
);

insert into public.topic_state (id, index)
values (1, 0)
on conflict (id) do nothing;

-- 3. Storage bucket for rendered videos
insert into storage.buckets (id, name, public)
values ('videos', 'videos', true)
on conflict (id) do nothing;

-- Allow the service-role key (used by CI) full access via RLS bypass.
-- The pipeline uses SUPABASE_SERVICE_KEY which bypasses RLS, so no
-- policies are required. If you later use the anon key, add policies here.
