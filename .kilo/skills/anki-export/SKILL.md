---
name: anki-export
description: Generate flashcards and quiz items from <topic>/knowledge/ and write them to <topic>/anki/<topic>.csv for Anki import. Use when the user runs /anki-export or wants Anki cards for a topic.
---

# Anki Export

Lifecycle step 4. Uses only `<topic>/knowledge/`.

## Steps

1. Identify the topic. If `<topic>/knowledge/` has no `.md` files, stop and say so.
2. Read the knowledge files. Do not add facts that are not in them.
3. Create items:
   - **Flashcards**: Front = a question or term; Back = the answer. Tag `<topic>::flashcard`.
   - **Quiz**: Front = a question with options or a fill-in, written as a single cell (e.g. `Q: ... A) ... B) ... C) ... D) ...`); Back = the correct answer plus a short explanation. Tag `<topic>::quiz`.
   - Each item should cite its source in Back as `(knowledge/<file>.md > <heading>)`.
   - Write in English. Keep Thai or other source-language terms exactly as in the source where they are names or technical terms.
4. Write `<topic>/anki/<topic>.csv`:
   - Header row: `Front,Back,Tags`
   - Tags are space-separated inside the Tags cell.
   - Use the `csv` module via a short Python command, or write with proper quoting. Fields containing commas, quotes, or newlines must be quoted; double internal quotes.
   - Encoding: UTF-8 with BOM (`utf-8-sig`) so Thai text reads correctly in Anki on Windows.
   - Overwrite the same file on each export (it is a generated artifact).
5. Report the file path and counts of flashcards and quiz items.

## Rules

- Do not invent facts beyond `knowledge/`. If coverage is thin, export fewer items and say so.
- Keep one fact per card.
