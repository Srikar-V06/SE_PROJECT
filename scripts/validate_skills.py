import pathlib
import re
import sys

errors = []
for f in pathlib.Path("skills").glob("*/SKILL.md"):
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        errors.append(f"{f}: missing frontmatter"); continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    if not name:
        errors.append(f"{f}: missing name")
    elif name.group(1).strip() != f.parent.name:
        errors.append(f"{f}: name must equal the folder name")
    if not desc:
        errors.append(f"{f}: missing description")
print("\n".join(errors) or "All SKILL.md files valid")
sys.exit(1 if errors else 0)