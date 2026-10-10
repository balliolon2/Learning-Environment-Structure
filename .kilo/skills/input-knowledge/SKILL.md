---
name: input-knowledge
description: Convert PDF, TXT, MD files, web URLs and YouTube links into Markdown in <topic>/knowledge/ using scripts/input_knowledge.py. Use when the user runs /input-knowledge or adds new study material to a topic.
---

# Input Knowledge

Lifecycle step 2. Loops with step 3 until the user says they are ready.

## Steps

1. Identify the topic. It must exist (`<topic>/` at repo root). If not, tell the user to run `/new-topic` first.
2. Collect sources:
   - Files the user placed in `<topic>/input-knowledge/` (or named explicitly). Never modify or delete them.
   - URLs or YouTube links the user pasted.
   - If the user gave none, list the files in `<topic>/input-knowledge/` and ask which to ingest.
3. Ensure the venv exists. If `.venv\Scripts\python.exe` is missing, run:
   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
4. Run the script with all sources in one call:
   ```
   .venv\Scripts\python scripts\input_knowledge.py <topic> <source> [<source> ...]
   ```
   Pass file names relative to `<topic>/input-knowledge/`, or URLs as-is.
5. Report each line of output: `OK: <path>` or `FAILED: <reason>`. For failures, state the reason and suggest a fix (e.g. scanned PDF, YouTube video without captions, page blocked). Do not hand-write Markdown to replace a failed source.
6. Tell the user they can run `/ask-any <topic> <question>` to test the knowledge.

## Rules

- Source-language text is kept as-is. Do not translate.
- Never invent knowledge content. The script is the only converter.
- Do not delete existing files in `knowledge/`; the script adds `-2`, `-3` suffixes on name clashes.
