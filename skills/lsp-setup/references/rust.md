# Rust notes for `lsp-setup`

Use this reference when the target repo is Rust or includes Rust crates.

## Install `rust-analyzer`

The most reliable install path is `rustup`:

```bash
curl https://sh.rustup.rs -sSf | sh
source "$HOME/.cargo/env"
rustup component add rust-analyzer
```

Always verify the executable, not just its presence on PATH:

```bash
command -v rust-analyzer
rust-analyzer --version
```

If `command -v rust-analyzer` succeeds but `rust-analyzer --version` fails, you likely have a
rustup shim without the component installed. Run:

```bash
rustup component add rust-analyzer
```

## Workspace root matters

Set `_REPO_ROOT` to the Cargo workspace root whenever possible.

That is especially important for:

- multi-crate workspaces
- `crates/*` layouts
- shared workspace dependencies
- cross-crate references and symbols

If the root is wrong, definitions, references, workspace symbols, and diagnostics can all degrade.

## Recommended allowlists

These are wrapper-policy settings, not LSP requirements.

Typical Rust defaults:

```python
_ALLOWED_DIRS = {"src", "crates", "tests", "examples", "benches"}
_ALLOWED_FILES = {"build.rs"}
```

Examples:

- single crate: `{"src", "tests", "examples", "benches"}`
- workspace: `{"crates", "tests", "examples", "benches"}`
- allow whole repo: `{"."}`

Use `{"."}` only when broad repo access is worth the tradeoff.

## Copy targets

For a Rust repo, copy:

- `assets/rust/dev.md` → `.fast-agent/agent-cards/dev.md`
- `assets/rust/rust_lsp_tools.py` → `.fast-agent/agent-cards/rust_lsp_tools.py`

Then update `_REPO_ROOT`, `_ALLOWED_DIRS`, and `_ALLOWED_FILES`.

## Smoke tests

After setup, start `fast-agent go` and try prompts like:

- `show me the symbols in crates/monty/src/lib.rs`
- `find the definition at line 12, character 8 in src/main.rs`
- `find references for the symbol at line 20, character 5 in src/lib.rs`

Adjust the path to a real `.rs` file in the repo.

## Validation

Basic validation steps:

```bash
python3 -m py_compile .fast-agent/agent-cards/rust_lsp_tools.py
fast-agent check
```

You should also confirm the Rust repo builds normally outside fast-agent, because
`rust-analyzer` depends on a sane Cargo workspace.

## Common failures

### `rust-analyzer` not found

Install it and verify:

```bash
rustup component add rust-analyzer
rust-analyzer --version
```

### `Path must live under...`

Expand `_ALLOWED_DIRS` / `_ALLOWED_FILES` to match the actual repo layout.

Common misses:

- `crates`
- `examples`
- `benches`
- `build.rs`

### Poor symbols, references, or diagnostics

Usually one of:

- `_REPO_ROOT` points at the wrong directory
- the Cargo workspace root is wrong
- dependencies or toolchain are not installed correctly
- the repo has multiple crates but only a subcrate root was used

### First request is slow

That is normal. The first request often pays server startup and indexing cost. Warm requests
should be much faster.

## Mixed-language repos

If the repo mixes Python, TypeScript, and Rust, prefer separate helper modules instead of one
giant dispatcher unless you really want a single shared tool surface.
