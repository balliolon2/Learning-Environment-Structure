# Learning-Environment-Structure

A learning environment for AI agent harnesses. Each study topic is a folder at the repo root. You study a topic through a fixed lifecycle: add sources, ask questions answered only from those sources, then export flashcards and quiz items to Anki.

The environment is plain files: Markdown knowledge, a Python ingestion script, and agent skills. It works with any harness that reads `AGENTS.md` and skill folders (Kilo is supported out of the box via `.kilo/`).

## Lifecycle

```
1. /new-topic <topic>
2. /input-knowledge <topic> [sources]   <-->   3. /ask-any <topic> <question>
                                              (repeat until you decide you are ready)
4. /anki-export <topic>
```

- Starting a new topic restarts at step 1.
- The loop between steps 2 and 3 ends when you decide, not the AI.

## Folder layout

```
AGENTS.md                 shared rules for all harnesses (lifecycle, language, folder conventions)
README.md                 this file
requirements.txt          Python dependencies for the ingestion script
scripts/
  input_knowledge.py      converts PDF, TXT/MD, web URLs and YouTube into Markdown
.skills/                  portable skills (harness-neutral), one folder per skill
  new-topic/SKILL.md
  input-knowledge/SKILL.md
  ask-any/SKILL.md
  anki-export/SKILL.md
.kilo/
  skills/                 Kilo copies of the same four skills
  command/                Kilo slash-command wrappers (/new-topic, /input-knowledge, /ask-any, /anki-export)
<topic>/                  one per study topic, created by /new-topic
  README.md               your learning goal and status checklist
  input-knowledge/        raw sources you add (PDF, TXT, MD). Never edited by the AI.
  knowledge/              generated Markdown. The only source for /ask-any and /anki-export.
  anki/                   exported CSV for Anki import
```

## Setup

Requires a Python 3 install on Windows.

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

`.venv/` and `__pycache__/` are git-ignored.

## Ingesting sources

```
.venv\Scripts\python scripts\input_knowledge.py <topic> <source> [<source> ...]
```

Each source is one of:

| Type | Example | Output |
|---|---|---|
| PDF or TXT/MD file | `lecture.pdf` (looked up in `<topic>/input-knowledge/`) or an absolute path | `<topic>/knowledge/lecture.md` |
| Web page | `https://example.com/article` | Main article text as Markdown |
| YouTube video | `https://www.youtube.com/watch?v=VIDEO_ID` or `https://youtu.be/VIDEO_ID` | Timestamped transcript (Thai, then English, when available) |

Each output file has front-matter with `source`, `type`, `title`, and `ingested_at`. Source-language text is kept as-is. On a name clash the script adds `-2`, `-3`, and so on instead of overwriting.

The script prints `OK: <path>` or `FAILED: <reason>` per source and exits non-zero if any source failed. Common failures:

- Scanned or image-only PDF: no extractable text.
- YouTube video without captions in the requested languages.
- Web page that cannot be downloaded or has no main content.

## Using the skills

Each skill lives in `.skills/<name>/SKILL.md` and has the same name and body as its Kilo copy. To use them in another harness, point it at `.skills/` as its skill directory, and make sure it reads `AGENTS.md` at the repo root.

In Kilo, use the slash commands from `.kilo/command/`: `/new-topic`, `/input-knowledge`, `/ask-any`, `/anki-export`.

`.skills/` and `.kilo/skills/` must stay identical. Edit both when changing a skill.

## Rules

- `AGENTS.md` is the shared rule file. Every harness should follow it.
- `/ask-any` and `/anki-export` use only `<topic>/knowledge/`. Gaps are reported, not filled from model memory.
- `/ask-any` answers are not saved to files.
- Anki CSV files are UTF-8 with BOM so Thai text imports correctly on Windows.
- Topic names are kebab-case: lowercase letters, digits, and hyphens.

## Anki import

Import `<topic>/anki/<topic>.csv` in Anki with the first row as field names. Columns are `Front`, `Back`, `Tags`. Flashcards are tagged `<topic>::flashcard`, quiz items `<topic>::quiz`.
