# Deployment workflows for Static Spaces

## 0) Local helper scripts (this skill)

Run helper scripts with `uv run` (PEP 723 script metadata):

```bash
uv run scripts/scaffold_static_space.py --space-id <username>/<space-name> --mode plain
uv run scripts/validate_static_space.py --space-id <username>/<space-name> --scope remote
```

---

## 1) CLI workflow (recommended quick path)

### Authenticate

```bash
uvx hf auth login
uvx hf auth whoami
```

### Create static Space

```bash
uvx hf repo create <username>/<space-name> \
  --repo-type space \
  --space-sdk static \
  --exist-ok
```

### Upload folder

```bash
uvx hf upload <username>/<space-name> ./<local-project-dir> \
  --repo-type space \
  --commit-message "Deploy static app"
```

### Sync mode (upload + delete removed files)

```bash
uvx hf upload <username>/<space-name> ./<local-project-dir> \
  --repo-type space \
  --delete="*" \
  --exclude=".git/*" \
  --commit-message "Sync static app"
```

---

## 2) Python API workflow

```python
from huggingface_hub import HfApi

repo_id = "<username>/<space-name>"
project_dir = "./<local-project-dir>"

api = HfApi()

api.create_repo(
    repo_id=repo_id,
    repo_type="space",
    space_sdk="static",
    exist_ok=True,
)

api.upload_folder(
    repo_id=repo_id,
    repo_type="space",
    folder_path=project_dir,
    commit_message="Deploy static app",
)

runtime = api.get_space_runtime(repo_id=repo_id)
print(runtime.stage, runtime.hardware)
```

---

## 3) Git remote workflow

```bash
git remote add space https://huggingface.co/spaces/<username>/<space-name>
git push --force space main
```

Use this when Space contents should exactly mirror Git history.

---

## 4) GitHub Actions workflow (repo mirror to Space)

Create `.github/workflows/sync-to-space.yml`:

```yaml
name: Sync to Hugging Face Space
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
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git push https://<username>:$HF_TOKEN@huggingface.co/spaces/<username>/<space-name> main
```

Requirements:
- Add `HF_TOKEN` in GitHub Secrets.
- Token must have write permissions.
