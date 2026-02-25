# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface_hub>=1.0.0",
# ]
# ///

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Findings:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_info(self, msg: str) -> None:
        self.info.append(msg)

    def ok(self) -> bool:
        return not self.errors




def _import_hf() -> tuple[object, object]:
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is required for remote validation. Run with `uv run scripts/validate_static_space.py ...` or install `huggingface_hub`."
        ) from exc
    return HfApi, hf_hub_download

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate HF Static Space config for local projects and/or deployed Spaces."
    )
    parser.add_argument("--space-id", help="Remote Space id, e.g. evalstate/foo")
    parser.add_argument("--project-dir", default=".", help="Local project directory (default: .)")
    parser.add_argument("--revision", default=None, help="Remote revision for --space-id")
    parser.add_argument("--token", default=None, help="HF token for private Spaces")
    parser.add_argument(
        "--strict-build-artifact",
        action="store_true",
        help="Require app_file to exist in repo/local path even when app_build_command is set",
    )
    parser.add_argument(
        "--scope",
        choices=("auto", "local", "remote", "both"),
        default="auto",
        help="What to validate: auto/local/remote/both (default: auto)",
    )
    return parser.parse_args()


def extract_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("README.md is missing YAML frontmatter opening '---'.")

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("README.md frontmatter is missing closing '---'.")

    meta: dict[str, str] = {}
    for raw in lines[1:end_idx]:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip("'").strip('"')
    return meta


def validate_static_metadata(meta: dict[str, str], findings: Findings) -> tuple[str, bool]:
    sdk = meta.get("sdk")
    if not sdk:
        findings.add_error("Missing required `sdk` in README frontmatter.")
    elif sdk != "static":
        findings.add_error(f"`sdk` must be `static` for this validator; found `{sdk}`.")

    app_file = meta.get("app_file")
    if not app_file:
        findings.add_error("Missing required `app_file` in README frontmatter.")
        app_file = ""

    has_build = bool(meta.get("app_build_command"))
    if has_build:
        findings.add_info(f"Detected build mode via app_build_command: {meta.get('app_build_command')}")
    else:
        findings.add_info("Detected plain static mode (no app_build_command).")

    if "base_path" in meta:
        findings.add_warning("`base_path` is for non-static Spaces. Prefer `app_file` for static Spaces.")

    return app_file, has_build


def load_local_readme(project_dir: Path) -> str:
    readme = project_dir / "README.md"
    if not readme.exists():
        raise FileNotFoundError(f"Missing README.md in {project_dir}")
    return readme.read_text(encoding="utf-8")


def local_validate(project_dir: Path, strict_build_artifact: bool) -> Findings:
    findings = Findings()
    try:
        readme_text = load_local_readme(project_dir)
        meta = extract_frontmatter(readme_text)
    except Exception as exc:
        findings.add_error(str(exc))
        return findings

    app_file, has_build = validate_static_metadata(meta, findings)
    if findings.errors:
        return findings

    app_path = project_dir / app_file
    if has_build:
        if app_path.exists():
            findings.add_info(f"Build artifact exists locally: {app_file}")
        elif strict_build_artifact:
            findings.add_error(f"Build mode but app_file not found locally: {app_file}")
        else:
            findings.add_warning(
                f"Build mode and app_file `{app_file}` not present locally (often OK before build)."
            )
    else:
        if app_path.exists():
            findings.add_info(f"Found app_file locally: {app_file}")
        else:
            findings.add_error(f"Plain mode requires app_file to exist locally, missing: {app_file}")

    return findings


def fetch_remote_readme(space_id: str, revision: str | None, token: str | None) -> str:
    _hf_api_cls, hf_hub_download = _import_hf()
    path = hf_hub_download(
        repo_id=space_id,
        repo_type="space",
        filename="README.md",
        revision=revision,
        token=token,
    )
    return Path(path).read_text(encoding="utf-8")


def remote_validate(
    space_id: str,
    revision: str | None,
    token: str | None,
    strict_build_artifact: bool,
) -> Findings:
    findings = Findings()
    hf_api_cls, _hf_hub_download = _import_hf()
    api = hf_api_cls(token=token)

    try:
        readme_text = fetch_remote_readme(space_id, revision, token)
        meta = extract_frontmatter(readme_text)
    except Exception as exc:
        findings.add_error(f"Failed loading remote README.md for {space_id}: {exc}")
        return findings

    app_file, has_build = validate_static_metadata(meta, findings)
    if findings.errors:
        return findings

    try:
        files = set(api.list_repo_files(repo_id=space_id, repo_type="space", revision=revision))
    except Exception as exc:
        findings.add_warning(f"Could not list remote files: {exc}")
        files = set()

    if files:
        if app_file in files:
            findings.add_info(f"app_file exists in repo: {app_file}")
        elif has_build and not strict_build_artifact:
            findings.add_warning(
                f"Build mode and app_file `{app_file}` not found in repo (can be normal if generated during build)."
            )
        else:
            findings.add_error(f"Configured app_file not found in repo: {app_file}")

    try:
        runtime = api.get_space_runtime(repo_id=space_id)
        findings.add_info(
            f"Runtime stage={runtime.stage}, hardware={runtime.hardware}, requested_hardware={runtime.requested_hardware}"
        )
        if "ERROR" in str(runtime.stage).upper():
            findings.add_warning(f"Space runtime indicates an error stage: {runtime.stage}")
    except Exception as exc:
        findings.add_warning(f"Could not fetch runtime for {space_id}: {exc}")

    return findings


def print_findings(label: str, findings: Findings) -> None:
    print(f"\n=== {label} ===")
    for msg in findings.info:
        print(f"[INFO] {msg}")
    for msg in findings.warnings:
        print(f"[WARN] {msg}")
    for msg in findings.errors:
        print(f"[ERROR] {msg}")

    if findings.ok():
        print("Result: PASS (no errors)")
    else:
        print("Result: FAIL (errors found)")


def resolve_scopes(args: argparse.Namespace, project_dir: Path) -> tuple[bool, bool]:
    if args.scope == "local":
        return True, False
    if args.scope == "remote":
        return False, True
    if args.scope == "both":
        return True, True

    # auto
    run_remote = bool(args.space_id)
    run_local = (project_dir / "README.md").exists() or not run_remote
    return run_local, run_remote


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    run_local, run_remote = resolve_scopes(args, project_dir)

    if run_remote and not args.space_id:
        raise SystemExit("--scope remote/both requires --space-id")

    local_findings: Findings | None = None
    remote_findings: Findings | None = None

    if run_local:
        local_findings = local_validate(project_dir, args.strict_build_artifact)
        print_findings("Local validation", local_findings)

    if run_remote and args.space_id:
        try:
            remote_findings = remote_validate(
                space_id=args.space_id,
                revision=args.revision,
                token=args.token,
                strict_build_artifact=args.strict_build_artifact,
            )
        except RuntimeError as exc:
            remote_findings = Findings()
            remote_findings.add_error(str(exc))
        print_findings(f"Remote validation ({args.space_id})", remote_findings)

    has_errors = False
    if local_findings and local_findings.errors:
        has_errors = True
    if remote_findings and remote_findings.errors:
        has_errors = True

    raise SystemExit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
