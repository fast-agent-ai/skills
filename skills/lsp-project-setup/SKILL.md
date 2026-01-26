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

### 1. Examine the Repository

Before copying files, examine the repo structure:

```bash
# List top-level directories
ls -d */

# Check for config files
ls pyproject.toml tsconfig.json package.json 2>/dev/null
```

Identify:
- **Language**: Python (pyproject.toml) or TypeScript (tsconfig.json)
- **Source directories**: Common patterns are `src/`, `lib/`, `app/`, `tests/`
- **Any existing `.fast-agent/` setup**

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

**Ripgrep search (recommended):**
- `assets/shared/ripgrep-search.md` → `.fast-agent/tool-cards/ripgrep-search.md`
- `assets/shared/fix_ripgrep_tool_calls.py` → `.fast-agent/hooks/fix_ripgrep_tool_calls.py`

### 4. Configure multilspy_tools.py

Edit `_ALLOWED_DIRS` based on the repo structure discovered in step 1:

```python
# Set to the actual source directories in this repo
_ALLOWED_DIRS = {"src", "tests"}  # ← Update based on step 1
```

Common patterns:
- Standard: `{"src", "tests"}`
- Monorepo: `{"packages", "apps", "libs"}`
- Flat: `{"."}` (entire repo - less secure)
- Django: `{"app", "apps", "tests"}`
- Library: `{"src", "lib", "tests", "examples"}`

Verify `_REPO_ROOT` is correct for the card location:
```python
# .fast-agent/agent-cards/ = 2 levels deep
_REPO_ROOT = Path(__file__).resolve().parents[2]
```

### 5. Configure Models

Edit `dev.md`:
```yaml
model: sonnet  # Your preferred model for development
```

Edit `ripgrep-search.md`:
```yaml
model: gpt-4o-mini  # Use cheap/fast model for search
```

### 6. Verify Setup

```bash
fast-agent go
```

Test with: "show me the symbols in src/main.py" (adjust path to actual file).

## Troubleshooting

Run `fast-agent check` to diagnose issues.

- **"ty is not available on PATH"**: Install ty (`uv tool install ty`)
- **"typescript-language-server is not available"**: Install via npm
- **"Path must live under..."**: Add the directory to `_ALLOWED_DIRS`
- **"Path is outside the repository root"**: Check `_REPO_ROOT` parents[] value
