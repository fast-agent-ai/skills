---
name: lsp-project-setup
description: LSP-enable a Python or TypeScript repository for fast-agent development. Use when setting up a new project with LSP code navigation tools, creating agent cards with LSP function tools, or configuring ty (Python) or typescript-language-server (TypeScript) integration.
---

# LSP Project Setup

Enable LSP-based code navigation in a repository by creating an agent card with LSP function tools.

## Prerequisites

- **Python**: `ty` language server (`uv tool install ty`)
- **TypeScript**: `typescript-language-server` (`npm install -g typescript-language-server typescript`)

The `multilspy` package is included with fast-agent.

## Setup Steps

### 1. Identify Language

Determine if the repo is Python or TypeScript:
- Python: has `pyproject.toml`, `setup.py`, or `requirements.txt`
- TypeScript: has `tsconfig.json` or `package.json` with TypeScript

### 2. Create Directory Structure

```bash
mkdir -p .fast-agent/agent-cards .fast-agent/tool-cards .fast-agent/hooks
```

### 3. Copy Template Files

Copy files from this skill's assets to `.fast-agent/`:

**Python:**
- `assets/python/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/python/multilspy_tools.py` → `.fast-agent/agent-cards/multilspy_tools.py`

**TypeScript:**
- `assets/typescript/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/typescript/multilspy_tools.py` → `.fast-agent/agent-cards/multilspy_tools.py`

**Ripgrep search (optional but recommended):**
- `assets/shared/ripgrep-search.md` → `.fast-agent/tool-cards/ripgrep-search.md`
- `assets/shared/fix_ripgrep_tool_calls.py` → `.fast-agent/hooks/fix_ripgrep_tool_calls.py`

### 4. Customize multilspy_tools.py

Edit the two constants at the top of `multilspy_tools.py`:

```python
# Adjust parents[] to match card depth from repo root
# .fast-agent/agent-cards/ = 2 levels deep, so parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Set directories the LSP can access (security boundary)
_ALLOWED_DIRS = {"src", "tests", "lib"}  # Customize for your repo
```

**`_REPO_ROOT`**: The `parents[N]` value depends on where the card lives:
- `.fast-agent/agent-cards/` → `parents[2]`
- `.dev/agent-cards/` → `parents[2]`
- `agent-cards/` → `parents[1]`

**`_ALLOWED_DIRS`**: Set to your source directories. Use `{"."}` for entire repo (less secure).

### 5. Customize Agent Cards

Edit `dev.md` frontmatter:

```yaml
model: sonnet  # Your preferred model

# To enable ripgrep search sub-agent:
agents: [ripgrep_search]

# Optional features
shell: true  # Enable shell commands
```

Edit `ripgrep-search.md` if using it:

```yaml
# Use a cheap/fast model for search - it runs frequently
model: gpt-4o-mini  # or: haiku, gemini-flash, local model
```

### 6. Verify Setup

Run from repo root:

```bash
fast-agent go
```

The agent should start with LSP tools available. Test with a query like "show me the symbols in src/main.py".

## Troubleshooting

Run `fast-agent check` to diagnose configuration issues.

- **"ty is not available on PATH"**: Install ty (`uv tool install ty`)
- **"typescript-language-server is not available"**: Install via npm
- **"Path must live under..."**: Expand `_ALLOWED_DIRS` in multilspy_tools.py
- **"Path is outside the repository root"**: Check `_REPO_ROOT` parents[] value
