# Run the video pipeline automatically on the cloud

Your phone setup (`scheduler.js` + `runner.js` + `agy` + Termux cron) can't
move to the cloud as-is because:

1. **`agy` doesn't exist on the cloud** — `runner.js` spawns an AI-agent CLI
   that only lives on your phone. The cloud path uses `scripts/cloud_pipeline.py`
   instead: deterministic, no agent needed.
2. **Termux paths** (`/data/data/com.termux/...`, `/sdcard/Download`) don't
   exist on Linux — font paths in all renderers are now fixed with fallbacks.
3. **`.pipeline/` is ephemeral on CI** — topic rotation state would reset
   every run. Supabase holds the state instead.

## Architecture

```
GitHub Actions (cron 12:30 & 19:30 EAT, + manual trigger)
  -> scripts/cloud_pipeline.py
       topic rotation (Supabase topic_state)
       -> .pipeline/script.json (11-scene template)
       -> render_engine.py (PIL + ffmpeg)
       -> scripts/review_video.py (QA score)
       -> Supabase Storage bucket `videos` (final.mp4)
       -> Supabase `jobs` table (log + rating)
  -> GitHub artifact backup (30 days)
```

Vercel is **not** used for rendering: serverless functions can't run ffmpeg
or render 870 frames within their timeout. Vercel is optional — you can
later add a small dashboard page that lists videos from Supabase.

## One-time setup (15 minutes)

### 1. Create the Supabase project
- Go to [supabase.com](https://supabase.com) → New project (free tier is fine).
- Open **SQL Editor → New query**, paste the contents of `supabase/schema.sql`, Run.
  This creates the `jobs` + `topic_state` tables and the `videos` storage bucket.

### 2. Get your Supabase keys
- Dashboard → **Settings → API**:
  - `Project URL` → `SUPABASE_URL`
  - `service_role` key → `SUPABASE_SERVICE_KEY` (keep it secret!)

### 3. Add GitHub Secrets
- GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY`
  - `SUPABASE_BUCKET` = `videos`

### 4. Push and test
- Push this branch to GitHub.
- GitHub repo → **Actions → Video Pipeline (Cloud) → Run workflow**.
- Watch it render (~5–10 min), then check:
  - Actions artifact `final-video-*` (downloadable video)
  - Supabase → Storage → `videos` bucket (uploaded video)
  - Supabase → Table Editor → `jobs` (run log + rating)

### 5. Automatic schedule
- No further action needed: the workflow runs daily at **09:30 UTC (12:30 EAT)**
  and **16:30 UTC (19:30 EAT)** — same times as your phone schedule.
- To change times, edit the `cron:` lines in `.github/workflows/video-pipeline.yml`
  (remember: GitHub cron is always UTC).

## Local test (before pushing)

```bash
# 1. Verify inputs without rendering
python3 scripts/cloud_pipeline.py --dry-run

# 2. Full render (needs ffmpeg: sudo apt install ffmpeg)
python3 scripts/cloud_pipeline.py
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ffmpeg not found` | Install it: `sudo apt install ffmpeg` (CI does this automatically) |
| `No usable bold font` | Install fonts: `sudo apt install fonts-dejavu-core` |
| Supabase upload 403/404 | Check bucket `videos` exists (run `supabase/schema.sql`) and the key is `service_role`, not `anon` |
| Workflow doesn't trigger on schedule | GitHub disables scheduled workflows after 60 days of no repo activity — push any commit to re-enable |
| Video renders but no audio | Ensure `video-engine/public/audio.mp3` exists in the repo |

## Phone vs cloud

- **Phone (Termux):** keep using `npm run schedule` / `crontab.txt` as before.
- **Cloud:** GitHub Actions + `scripts/cloud_pipeline.py`. Don't run both at
  the same time or you'll get duplicate videos and topic rotation will drift.
