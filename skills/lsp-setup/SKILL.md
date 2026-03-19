---
name: lsp-setup
description: LSP-enable a Python, TypeScript, or Rust repository for fast-agent development. Use when creating or refreshing agent cards with LSP function tools, configuring ty, typescript-language-server, or rust-analyzer integration, or scoping repo-local code navigation safely.
---

# LSP Setup

Enable LSP-based code navigation in a repository by creating an agent card with LSP function tools.

## Prerequisites

- **Python**: `ty` language server (`uv tool install ty`)
- **TypeScript**: `typescript-language-server` (`npm install -g typescript-language-server typescript`)
- **Rust**: `rust-analyzer` (`rustup component add rust-analyzer`)

The `multilspy` package is included with fast-agent.

## Setup Steps

### 1. Examine the Repository

Before copying files, inspect the repo root:

```bash
ls -d */
ls pyproject.toml tsconfig.json package.json 2>/dev/null
ls Cargo.toml 2>/dev/null
```

Identify:

- **Language**: Python (`pyproject.toml`), TypeScript (`tsconfig.json`), or Rust (`Cargo.toml`)
- **Source directories**: Common patterns are `src/`, `lib/`, `app/`, `tests/`, `packages/`, `apps/`, `crates/`, `examples/`, `benches/`
- **Root-level files you may want to query**: `setup.py`, `manage.py`, `conftest.py`, `build.rs`, etc.
- **Any existing `.fast-agent/` setup**

### 2. Create Directory Structure

**IMPORTANT** -- by default the environment directory is `.fast-agent`, but use the environment directory specified earlier if different.

```bash
mkdir -p .fast-agent/agent-cards
```

### 3. Copy Template Files

Copy files from this skill's assets to `.fast-agent/agent-cards/`.

**Python:**

- `assets/python/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/python/multilspy_tools.py` → `.fast-agent/agent-cards/multilspy_tools.py`

**TypeScript:**

- `assets/typescript/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/typescript/multilspy_tools.py` → `.fast-agent/agent-cards/multilspy_tools.py`

**Rust:**
- `assets/rust/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/rust/rust_lsp_tools.py` → `.fast-agent/agent-cards/rust_lsp_tools.py`

### 4. Configure the helper module

For Python and TypeScript, configure `multilspy_tools.py`.
For Rust, configure `rust_lsp_tools.py`.

There are two different configuration steps:

#### Required: verify `_REPO_ROOT`

The LSP server normally just needs the correct repo root as `cwd` / `rootUri` to work well.
Make sure `_REPO_ROOT` matches where you placed the card:

```python
# .fast-agent/agent-cards/ = 2 levels below repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]
```

If you place the card somewhere else, adjust `parents[...]` accordingly.

#### Recommended: set `_ALLOWED_DIRS` and `_ALLOWED_FILES`

These settings are **wrapper policy**, not an LSP requirement. They control what files the tool is allowed to query.

```python
_ALLOWED_DIRS = {"src", "tests"}
_ALLOWED_FILES = {"conftest.py"}
```

Common patterns:

- Standard Python: `{"src", "tests", "test", "examples"}`
- Standard TypeScript: `{"src"}`
- Monorepo: `{"packages", "apps", "libs"}`
- Django: `{"app", "apps", "tests"}` + `{"manage.py"}`
- Flat repo / allow entire repo: `{"."}`

Use narrower allowlists when possible. Use `{"."}` only when whole-repo access is worth the tradeoff.

#### Rust note

For Rust, always verify the executable itself, not just its PATH entry:

```bash
command -v rust-analyzer
rust-analyzer --version
```

Use the Cargo workspace root for `_REPO_ROOT` whenever possible, especially for `crates/*` layouts.

### 5. Optional: Wire in Search Separately

This skill only sets up the LSP tools. If you want broad text/file discovery, add your preferred search card or tool separately.

For deeper Rust setup and troubleshooting notes, see [references/rust.md](references/rust.md).

### 6. Verify Setup

```bash
fast-agent go
```

Try:

- `show me the symbols in src/main.py`
- `find the definition of Foo in src/foo.py at line 12`
- `show me the symbols in crates/my_crate/src/lib.rs`

Adjust the path to a real file in the repo.

## Troubleshooting

Run `fast-agent check` to diagnose issues.

- **"ty is not available on PATH"**: Install ty (`uv tool install ty`)
- **"typescript-language-server is not available"**: Install via npm
- **"rust-analyzer is not available on PATH"**: Install it with `rustup component add rust-analyzer`
- **"Path must live under..."**: Update `_ALLOWED_DIRS` or `_ALLOWED_FILES`
- **"Path is outside the repository root"**: Check `_REPO_ROOT`
- **LSP starts but results are poor**: Confirm the repo root has the right `pyproject.toml`, `tsconfig.json`, workspace layout, and dependencies
