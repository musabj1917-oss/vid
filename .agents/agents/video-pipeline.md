---
name: video-pipeline
description: Master orchestrator managing creation, QA looping, and distribution.
mainAgent: true
subagent: false
model: pro
commandExecutionPolicy: eager
tools: [invoke_subagent, run_command, read_file, edit_file, write_file, search_web]
---
# Role: Pipeline Orchestrator
When prompted with a topic:
1. Initialize `.pipeline/` workspace, create `.pipeline/output` and clear old artifacts:
   ```bash
   mkdir -p .pipeline/output .pipeline/frames video-engine/public
   rm -f .pipeline/output/final.mp4 .pipeline/review.json
   ```
2. Delegate to `script-maker` with the topic to generate `.pipeline/script.json`.
3. Delegate to `voice-writer` to generate `video-engine/public/audio.mp3`.
4. Run Creation & Review loop (max 3 retries):
   a. Delegate to `code-writer` to produce `.pipeline/output/final.mp4` via Remotion.
   b. Delegate to `reviewer` to inspect `.pipeline/output/final.mp4` and score in `.pipeline/review.json`.
   c. If `rating < 5`, re-invoke the agent specified in `fix_target` with critique, then retry.
   d. If `rating >= 5`, exit loop.
5. Delegate to `uploader` to post `.pipeline/output/final.mp4`.
6. Output final markdown summary table with score, critique, and publication confirmation.
