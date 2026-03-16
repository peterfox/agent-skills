# Agent Skills — Development Guide

This repo contains Claude Code skills for PHP development workflows. Skills are packaged as `.skill` files for distribution.

## Project Structure

```
agent-skills/
├── <skill-name>/          # Skill source directory
│   ├── SKILL.md           # Required: frontmatter + instructions
│   ├── references/        # Optional: reference docs loaded as needed
│   ├── scripts/           # Optional: executable scripts
│   └── assets/            # Optional: templates, images, etc.
├── <skill-name>.skill     # Packaged distributable (zip with .skill extension)
├── package-all.sh         # Packages all skills in the repo
└── README.md
```

## Developing a Skill

### 1. Initialize

Use the `init_skill.py` script from the `skill-creator` skill to scaffold a new skill:

```bash
python3 ~/.claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .
```

This creates a `<skill-name>/` directory with a `SKILL.md` template and example resource directories.

### 2. Edit SKILL.md

Every `SKILL.md` requires YAML frontmatter with `name` and `description`:

```markdown
---
name: my-skill
description: What this skill does and when it should trigger. Include trigger phrases and use cases here.
---

# Skill Title

Instructions for Claude...
```

- The `description` is the primary trigger mechanism — be specific about when the skill should activate
- Keep the body under 500 lines; move detailed content to `references/` files
- Reference files from `SKILL.md` with clear guidance on when to read them

### 3. Add Resources

- **`references/`** — Documentation Claude reads when needed (schemas, API docs, patterns)
- **`scripts/`** — Deterministic scripts for repeated operations; test them before packaging
- **`assets/`** — Templates and files used in output (not loaded into context)

Delete any example files from `init_skill.py` that aren't needed.

## Reviewing an Existing Skill

When asked to review or improve a skill, read all files in the skill directory before making any changes: `SKILL.md` and every file in `references/`, `scripts/`, and `assets/`. Then look for:

- **Duplication between SKILL.md and reference files** — content that appears in both should live only in the reference file, with SKILL.md reduced to a one- or two-line pointer
- **Duplication across reference files** — consolidate or add cross-references
- **Over-explained content** — remove prose that restates what a code example already shows clearly; trust that Claude can read code
- **Long sections that belong in references** — any section in SKILL.md approaching 20+ lines on a single sub-topic is a candidate to move to a dedicated reference file
- **Sections with no cross-reference** — every reference file should be mentioned from SKILL.md with guidance on when to read it; orphaned reference files won't get used

When trimming, preserve the key decision rules and non-obvious patterns. What gets cut is repetition, verbose explanation of self-evident code, and content that is already comprehensively covered elsewhere.

## Packaging a Skill

Package a single skill:

```bash
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py <skill-name>/
```

Package all skills in the repo:

```bash
./package-all.sh
```

The packaging script validates the skill first (frontmatter, naming, structure) then creates `<skill-name>.skill` in the project root. Fix any validation errors and re-run.

## Key Principles

- **Concise is key** — only include context Claude doesn't already have
- **Progressive disclosure** — metadata triggers, SKILL.md body loads on trigger, references load as needed
- **No extra docs** — don't create README, CHANGELOG, or other auxiliary files inside a skill directory; the skill should only contain what an AI agent needs to do the job
