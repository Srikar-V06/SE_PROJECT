import re
import sys
from pathlib import Path

import yaml

required_fields = {
    "title",
    "type",
    "status",
    "created",
    "updated",
    "author",
    "tags",
    "sources",
    "links",
    "requirements",
}

errors = []

notes = [
    path
    for path in Path("brain").rglob("*.md")
    if path.name not in {"index.md", "log.md"}
]

index_text = Path("brain/index.md").read_text(encoding="utf-8")

for path in notes:
    text = path.read_text(encoding="utf-8")

    match = re.match(
        r"^---\r?\n(.*?)\r?\n---",
        text,
        re.DOTALL,
    )

    if not match:
        errors.append(f"{path}: missing frontmatter")
        continue

    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        errors.append(f"{path}: invalid YAML frontmatter")
        continue

    if not isinstance(metadata, dict):
        errors.append(f"{path}: invalid metadata")
        continue

    missing = required_fields - metadata.keys()

    if missing:
        errors.append(f"{path}: missing fields {sorted(missing)}")

    if metadata.get("type") not in (
        "project", "area", "resource", "archive", "inbox"
    ):
        errors.append(f"{path}: invalid note type")

    if metadata.get("status") not in ("draft", "active", "done"):
        errors.append(f"{path}: invalid status")

    for field in ("tags", "sources", "links", "requirements"):
        if not isinstance(metadata.get(field), list):
            errors.append(f"{path}: {field} must be a list")

    if not metadata.get("links"):
        errors.append(f"{path}: no related note links")

    if f"[[{path.stem}]]" not in index_text:
        errors.append(f"{path}: missing from brain/index.md")

    if metadata.get("type") == "resource":
        body = text[match.end():]

        for heading in (
            "## Summary",
            "## Key points",
            "## Relevance to this project",
        ):
            if heading not in body:
                errors.append(f"{path}: missing {heading}")

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("Brain schema audit passed")