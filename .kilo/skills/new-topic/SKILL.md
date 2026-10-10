---
name: new-topic
description: Create a new learning topic folder with input-knowledge/, knowledge/, anki/ and a README learning goal. Use when the user runs /new-topic or wants to start studying a new subject.
---

# New Topic

Lifecycle step 1. Creates a topic at the repo root.

## Steps

1. Get the topic name from the user. Must be kebab-case: lowercase letters, digits, hyphens (e.g. `rust-ownership`). If it is not, propose a corrected name and ask once.
2. If `<topic>/` already exists, stop and tell the user. Do not overwrite.
3. Ask the user for the learning goal in one short question (what they want to be able to do after studying). Skip if already given.
4. Create:
   - `<topic>/input-knowledge/`
   - `<topic>/knowledge/`
   - `<topic>/anki/`
   - `<topic>/README.md` using the template below.
5. Tell the user the next step: `/input-knowledge <topic> [sources]`.

## README template

```markdown
# <Topic title>

## Learning goal
<goal from the user>

## Structure
- input-knowledge/: raw sources (PDF, TXT, MD), never edited by the AI
- knowledge/: generated Markdown; the only source for /ask-any and /anki-export
- anki/: exported CSV files for Anki import

## Status
- [ ] Input knowledge
- [ ] Study with /ask-any
- [ ] Anki export
```

Create the folders and the README with whatever file tools the harness provides. Do not create any other files.
