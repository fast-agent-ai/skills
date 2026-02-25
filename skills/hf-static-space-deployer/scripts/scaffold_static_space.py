# /// script
# requires-python = ">=3.10"
# ///

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

VALID_COLORS = {"red", "yellow", "green", "blue", "indigo", "purple", "pink", "gray"}
SPACE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class Config:
    project_dir: Path
    space_id: str
    mode: str  # plain | build
    title: str
    emoji: str
    color_from: str
    color_to: str
    app_file: str
    build_command: str | None
    commit_message: str
    private: bool
    write_workflow: bool
    workflow_path: Path
    overwrite: bool
    dry_run: bool


def _yaml_quote(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Scaffold README metadata + optional GitHub Action for Hugging Face Static Spaces."
    )
    parser.add_argument("--project-dir", default=".", help="Local project directory (default: .)")
    parser.add_argument("--space-id", required=True, help="Hugging Face Space ID, e.g. username/my-space")
    parser.add_argument(
        "--mode",
        choices=("plain", "build"),
        default="plain",
        help="plain=index.html already exists, build=use app_build_command (default: plain)",
    )
    parser.add_argument("--title", default="My Static Space", help="Space title")
    parser.add_argument("--emoji", default="🌐", help="Space emoji")
    parser.add_argument("--color-from", default="blue", help=f"One of: {', '.join(sorted(VALID_COLORS))}")
    parser.add_argument("--color-to", default="indigo", help=f"One of: {', '.join(sorted(VALID_COLORS))}")
    parser.add_argument("--app-file", default=None, help="Path to entry HTML (relative to repo root)")
    parser.add_argument("--build-command", default="npm run build", help="Build command for --mode build")
    parser.add_argument("--commit-message", default="Deploy static app", help="Commit message for hf upload")
    parser.add_argument("--private", action="store_true", help="Use --private on hf repo create command")
    parser.add_argument(
        "--write-workflow",
        action="store_true",
        help="Write .github/workflows/sync-to-space.yml",
    )
    parser.add_argument(
        "--workflow-path",
        default=".github/workflows/sync-to-space.yml",
        help="Workflow path relative to project-dir",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite README/workflow if they exist")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")

    ns = parser.parse_args()

    if not SPACE_ID_RE.match(ns.space_id):
        raise SystemExit(f"Invalid --space-id '{ns.space_id}'. Expected format: username/space-name")

    color_from = ns.color_from.strip().lower()
    color_to = ns.color_to.strip().lower()
    if color_from not in VALID_COLORS:
        raise SystemExit(f"Invalid --color-from '{ns.color_from}'.")
    if color_to not in VALID_COLORS:
        raise SystemExit(f"Invalid --color-to '{ns.color_to}'.")

    app_file = ns.app_file
    if app_file is None:
        app_file = "index.html" if ns.mode == "plain" else "dist/index.html"

    build_command = ns.build_command if ns.mode == "build" else None

    return Config(
        project_dir=Path(ns.project_dir).resolve(),
        space_id=ns.space_id,
        mode=ns.mode,
        title=ns.title,
        emoji=ns.emoji,
        color_from=color_from,
        color_to=color_to,
        app_file=app_file,
        build_command=build_command,
        commit_message=ns.commit_message,
        private=ns.private,
        write_workflow=ns.write_workflow,
        workflow_path=Path(ns.workflow_path),
        overwrite=ns.overwrite,
        dry_run=ns.dry_run,
    )


def build_readme(cfg: Config) -> str:
    lines = [
        "---",
        f"title: {_yaml_quote(cfg.title)}",
        f"emoji: {_yaml_quote(cfg.emoji)}",
        f"colorFrom: {_yaml_quote(cfg.color_from)}",
        f"colorTo: {_yaml_quote(cfg.color_to)}",
        "sdk: static",
    ]
    if cfg.build_command:
        lines.append(f"app_build_command: {_yaml_quote(cfg.build_command)}")
    lines.append(f"app_file: {_yaml_quote(cfg.app_file)}")
    lines.append("pinned: false")
    lines.append("---")
    lines.append("")
    lines.append(f"# {cfg.title}")
    lines.append("")
    lines.append("Deployed as a Hugging Face Static Space.")
    lines.append("")
    return "\n".join(lines)


def build_workflow(space_id: str) -> str:
    user, _space_name = space_id.split("/", 1)
    return f"""name: Sync to Hugging Face Space
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  sync-to-space:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          lfs: true

      - name: Push to Space
        env:
          HF_TOKEN: ${{{{ secrets.HF_TOKEN }}}}
        run: |
          git push https://{user}:$HF_TOKEN@huggingface.co/spaces/{space_id} main
"""


def write_text(path: Path, content: str, overwrite: bool, dry_run: bool) -> None:
    if dry_run:
        if path.exists() and not overwrite:
            print(f"[dry-run] Would skip existing file (use --overwrite): {path}")
        else:
            print(f"[dry-run] Would write: {path}")
        return
    if path.exists() and not overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {path} (use --overwrite)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Wrote: {path}")


def print_next_steps(cfg: Config) -> None:
    create_cmd = [
        "uvx",
        "hf",
        "repo",
        "create",
        cfg.space_id,
        "--repo-type",
        "space",
        "--space-sdk",
        "static",
        "--exist-ok",
    ]
    if cfg.private:
        create_cmd.append("--private")

    upload_cmd = [
        "uvx",
        "hf",
        "upload",
        cfg.space_id,
        str(cfg.project_dir),
        "--repo-type",
        "space",
        "--commit-message",
        cfg.commit_message,
    ]

    print("\nNext steps:")
    print("1) Authenticate")
    print("   uvx hf auth login")
    print("\n2) Create/ensure Space")
    print("   " + " ".join(shlex.quote(x) for x in create_cmd))
    print("\n3) Upload project")
    print("   " + " ".join(shlex.quote(x) for x in upload_cmd))
    print("\n4) Open Space")
    print(f"   https://huggingface.co/spaces/{cfg.space_id}")


def main() -> None:
    cfg = parse_args()

    readme_path = cfg.project_dir / "README.md"
    readme = build_readme(cfg)
    write_text(readme_path, readme, overwrite=cfg.overwrite, dry_run=cfg.dry_run)

    if cfg.write_workflow:
        workflow_full = cfg.project_dir / cfg.workflow_path
        workflow = build_workflow(cfg.space_id)
        write_text(workflow_full, workflow, overwrite=cfg.overwrite, dry_run=cfg.dry_run)

    print_next_steps(cfg)


if __name__ == "__main__":
    main()
