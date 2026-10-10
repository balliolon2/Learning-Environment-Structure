# Learning Environment

This repo is a learning environment. Each topic is a folder at the repo root. The user studies a topic through a fixed lifecycle, driven by skills in `.kilo/skills/`.

## Lifecycle

```
1. /new-topic <topic>
2. /input-knowledge <topic> [sources]   <-->   3. /ask-any <topic> <question>
                                              (repeat until the user decides they are ready)
4. /anki-export <topic>
```

- Starting a new topic restarts at step 1.
- The loop between steps 2 and 3 ends when the user says so. Never decide "ok" on the user's behalf.

## Topic layout

```
<topic>/
  README.md           learning goal and structure
  input-knowledge/    raw sources: .pdf, .txt, .md (user-provided; never delete)
  knowledge/          generated Markdown, the ONLY source for /ask-any and /anki-export
  anki/               exported CSV files for Anki import
```

## Tooling

- Ingestion script: `scripts/input_knowledge.py`
- Dependencies: `requirements.txt` (pypdf, trafilatura, youtube-transcript-api)
- Virtualenv: `.venv/` in the repo root (git-ignored)
- Setup once:
  ```
  python -m venv .venv
  .venv\Scripts\python -m pip install -r requirements.txt
  ```
- Run:
  ```
  .venv\Scripts\python scripts\input_knowledge.py <topic> <source> [<source> ...]
  ```

## Rules

1. Language: all instructions, skills, and AI responses are in English. Knowledge files keep the language of their source. Do not translate source content.
2. `/ask-any` and `/anki-export` use only content in `<topic>/knowledge/`. Do not fill gaps from model memory. If the knowledge does not contain the answer, say so and name what kind of source would fill the gap.
3. `/ask-any` cites every claim as `knowledge/<file>.md` plus the nearest heading or page marker. Answers are not saved to files.
4. Do not modify or delete anything in `<topic>/input-knowledge/`.
5. Do not invent knowledge files by hand for sources the script could not convert. Report the failure instead.
6. Topic names are kebab-case: lowercase letters, digits, and hyphens.
