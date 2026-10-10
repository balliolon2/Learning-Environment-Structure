# Learning Environment: Skills + AGENTS.md Plan

## Goal
Build a project-level learning environment (similar in spirit to a harness) driven by Kilo skills and a root `AGENTS.md`. The user moves through a lifecycle per topic:

```
1 /new-topic  ->  2 /input-knowledge <topic>  <-->  3 /ask-any <topic>  (loop, user decides)  ->  4 /anki-export <topic>
```

Starting a new topic restarts at step 1.

## Decisions (resolved)
| Area | Decision |
|---|---|
| Location | Project-level. Skills in `.kilo/skills/<name>/SKILL.md`. Topics are sibling folders at repo root. |
| Knowledge format | Markdown only. No RAG/vector DB. |
| Ingestion | One Python script handles PDF, TXT, URL, and YouTube, and writes Markdown into `<topic>/knowledge/`. |
| Python libs | `pypdf`, `trafilatura`, `youtube-transcript-api`. Pinned in `requirements.txt`. |
| Python env | `.venv/` inside repo. Install via `pip install -r requirements.txt`. |
| Loop exit (2 <-> 3) | User decides by feel. AI does not decide "ok". |
| /ask-any answers | Only from `knowledge/`. Every claim cites file path + heading. If knowledge lacks the answer, say so; do not fill from model memory. Answers are not saved to files. |
| /anki-export format | CSV with columns `Front,Back,Tags`. Flashcards and quiz items are both rows. Tags separate them: `<topic>::flashcard` and `<topic>::quiz`. Quiz is a question on Front with the answer on Back. |
| Language | AGENTS.md, skills, and all AI output (including /ask-any and Anki) in English. Knowledge files keep the source language (e.g., Thai PDF stays Thai). |
| /new-topic scaffold | Creates `<topic>/input-knowledge/`, `<topic>/knowledge/`, `<topic>/README.md` (learning goal + standard structure). |

## Layout to create
```
AGENTS.md                         # lifecycle rules, language, conventions
requirements.txt                  # pypdf, trafilatura, youtube-transcript-api
scripts/input_knowledge.py        # single ingestion script
.kilo/skills/new-topic/SKILL.md
.kilo/skills/input-knowledge/SKILL.md
.kilo/skills/ask-any/SKILL.md
.kilo/skills/anki-export/SKILL.md
<topic>/input-knowledge/          # raw inputs (created by /new-topic)
<topic>/knowledge/                # generated Markdown (created by /new-topic)
<topic>/README.md                 # learning goal + structure (created by /new-topic)
```

## Ordered tasks
1. Create `requirements.txt` with the three libraries (version-unpinned or pinned; pin at install time).
2. Implement `scripts/input_knowledge.py`:
   - Args: `<topic> <source>` where source is a file path (.pdf/.txt) or URL, or a YouTube URL.
   - Detect type by extension / URL host (`youtube.com`, `youtu.be` -> YouTube).
   - Write output to `<topic>/knowledge/<slug>.md` with front-matter: `source`, `type`, `ingested_at`.
   - Keep original source language. Do not translate.
   - Do not overwrite existing files silently; append suffix or exit with message.
   - Exit non-zero with a clear message on failure (encrypted PDF, no transcript, fetch error).
3. Write `AGENTS.md` at repo root: lifecycle, folder conventions, language rules, venv command (`.venv\Scripts\python scripts\input_knowledge.py ...`), and the rule that `/ask-any` answers only from `knowledge/`.
4. Write the four skill files in `.kilo/skills/<name>/SKILL.md` with frontmatter `name` and `description`:
   - `new-topic`: validate topic name (kebab-case, not existing), create folders and README.
   - `input-knowledge`: take files/URLs from `input-knowledge/` or pasted in chat; run script; report created files; loop-friendly.
   - `ask-any`: read `knowledge/*.md`; answer in English with citations `file.md#heading`; say when knowledge is insufficient.
   - `anki-export`: read `knowledge/`; generate flashcards + quiz rows; write `<topic>/anki/<topic>.csv`; use `Front,Back,Tags` with a header row, UTF-8 with BOM for Anki on Windows.
5. Verify slash invocation: check whether `/new-topic` etc. resolve from `.kilo/skills`. If not, add thin wrappers in `.kilo/command/<name>.md` that invoke the skill. This is the only open technical point.
6. Validation:
   - `pip install -r requirements.txt` into `.venv` succeeds.
   - Run script on a sample TXT, a sample PDF, one web URL, and one YouTube URL with captions; confirm Markdown output.
   - Dry-run `/new-topic` on a test topic, then delete it.
   - Run `/ask-any` on a question present in knowledge (expect citation) and one absent (expect "not in knowledge").
   - Run `/anki-export`, open the CSV in Anki import, confirm columns map and Thai text renders.

## Risks / edge cases
- YouTube videos without captions: script must fail clearly; no fallback to model memory.
- Scanned PDFs (image-only): pypdf returns empty text; script should report "no extractable text" rather than produce empty markdown.
- Commas/newlines in CSV content: use the `csv` module, not string concatenation.
- Thai text in CSV: UTF-8 with BOM so Anki on Windows reads it correctly.
- Script not run before ask-any: ask-any only sees what is already in `knowledge/`.

## Out of scope
- RAG/embeddings, vector DB, web UI, automatic spaced-repetition scheduling, translation of knowledge, saving /ask-any answers.

## Open items for implementation agent
- Confirm skill-to-slash-command mapping (task 5). Everything else is decided.
- Known issue from implementation: the config validator rejects `.kilo/command/*.md` with `Failed to parse frontmatter: No context found for instance`. The frontmatter follows the kilo-config reference. Verify whether `/new-topic` works at all before keeping the wrappers.

## Phase 2: portable skills for other harnesses (planning)

### Goal
Provide the same lifecycle (`new-topic`, `input-knowledge`, `ask-any`, `anki-export`) to other agent harnesses that use this repo structure, and update `README.md` (currently one line) to document the whole environment.

### Current state (verified)
- Skills exist only under `.kilo/skills/<name>/SKILL.md`.
- `AGENTS.md` at repo root is the lifecycle rule source.
- `README.md` contains only `# Learning-Environment-Structure`.

### Decision (resolved)
Option A: `.skills/<name>/SKILL.md` is the portable, harness-neutral copy. `.kilo/skills/` stays for Kilo.
- Rejected B (symlink/junction): needs Windows developer mode or admin.
- Rejected C (no new folder): other harnesses would have to read `.kilo/`.

### Sync rule
- The four `SKILL.md` bodies in `.skills/` and `.kilo/skills/` are identical. Only the file location differs.
- Write bodies harness-neutral from the start so no Kilo-only text exists in either copy:
  - No tool names such as `question`, `todowrite`, `write`, `mkdir`. Use "create files/folders", "ask the user".
  - No "Load the skill" wording. That stays in `.kilo/command/*.md` only.
- The `.kilo/command/*.md` wrappers remain Kilo-only and are not copied.

### Language
README.md is in English, matching the AGENTS.md rule. Thai-speaking users are not addressed in the README body.

### Tasks
1. Create `.skills/new-topic/SKILL.md`, `.skills/input-knowledge/SKILL.md`, `.skills/ask-any/SKILL.md`, `.skills/anki-export/SKILL.md` with the same frontmatter (`name`, `description`) and body as the `.kilo/skills` copies, after making the neutral-wording edits above to both copies.
2. Write `README.md` (replace the one-line file) with these sections, in order:
   - Purpose (one paragraph)
   - Lifecycle diagram (copy from AGENTS.md)
   - Folder layout (repo root, `<topic>/`, `scripts/`, `.skills/`, `.kilo/`)
   - Setup: `python -m venv .venv`, `.venv\Scripts\python -m pip install -r requirements.txt`
   - Script usage: `.venv\Scripts\python scripts\input_knowledge.py <topic> <source> [<source> ...]`, with the three source types
   - Using the skills: point the harness at `.skills/` (generic), or use `.kilo/command/` for Kilo slash commands
   - Note: AGENTS.md is the shared rule file for all harnesses
3. Validation:
   - `Compare-Object` (or diff) between `.skills/*/SKILL.md` and `.kilo/skills/*/SKILL.md`: must be empty.
   - Each frontmatter has `name` equal to its folder name and a non-empty `description`.
   - Grep the `.skills/` tree for `Kilo`, `question`, `todowrite`, `Load the`: must find nothing.
   - README commands match `scripts/input_knowledge.py` argparse (`topic`, `sources`).
   - Verify the `.kilo/command` slash-command question (see open items) separately; it does not block the README.

### Out of scope
- Automatic harness detection or installers.
- Changing lifecycle behavior.
- Fixing the `.kilo/command` validator error (tracked in open items).
