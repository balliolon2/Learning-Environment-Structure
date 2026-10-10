---
name: ask-any
description: Answer a question about a topic using only the Markdown files in <topic>/knowledge/, with file and heading citations, like NotebookLM. Use when the user runs /ask-any or asks a question about a study topic.
---

# Ask Any

Lifecycle step 3. Answers are only given from `<topic>/knowledge/`.

## Steps

1. Identify the topic. If `<topic>/knowledge/` is missing or has no `.md` files, say so and suggest `/input-knowledge <topic>`. Stop.
2. Read the relevant files in `<topic>/knowledge/` (use grep to locate the question's terms, then read the matching sections). Read all files if the knowledge base is small.
3. Answer in English, even if the question is in Thai or another language.
4. Cite every claim as `knowledge/<file>.md` plus the nearest heading or page marker, e.g. `knowledge/rust-book.md > ## Ownership` or `knowledge/paper.md > ## Page 4`.
5. If the knowledge does not contain the answer:
   - Say so plainly.
   - Name the kind of source that would fill the gap (e.g. "a chapter on X from a textbook", "the official API reference for Y").
   - Do not answer from model memory.
6. Do not save the answer to any file.

## Rules

- Partial coverage: answer the covered part with citations and list what is missing.
- Contradictions between sources: show both with citations; do not pick one silently.
- The user decides when the loop with step 2 ends. Do not suggest that the topic is "done".
