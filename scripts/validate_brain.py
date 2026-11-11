import sys, pathlib, re
notes = list(pathlib.Path("brain").rglob("*.md"))
names = {n.stem for n in notes}
errors = []
for n in notes:
    text = n.read_text(encoding="utf-8")
    if n.name not in ("index.md", "log.md") and not text.startswith("---"):
        errors.append(f"{n}: missing frontmatter")
    for link in re.findall(r"\[\[([^\]]+)\]\]", text):
        target = re.split(r"[|#]", link)[0].strip()
        if target and target not in names:
            errors.append(f"{n}: broken link [[{link}]]")
print("\n".join(errors) or "All brain notes valid")
sys.exit(1 if errors else 0)