"""Check a bootstrapped installation using markdown-it-py. Print TSV to stdout.

Include referenced evidence files in the fixture without following their links.
Pass --request separately to check the active migration documents at their real paths.
"""
import argparse
import csv
import hashlib
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


PARSER = MarkdownIt().enable("table")
PACKAGES = ("common", "project")
ARCHIVE_DIRS = ("inbox", "handoffs", "docs/plans", "testing/evidence",
                "testing/evidence/work", "testing/evidence/harness")
EXCLUDED = {Path("harness", package, name) for package in PACKAGES for name in ARCHIVE_DIRS}
SKIP = {".pytest_cache", "__pycache__", ".git", ".venv", "node_modules"}
ROOT_PATH = re.compile(r"(?:harness/(?:common|project)(?:/[\w.\-]+)*/?|\.claude/rules/?)$")


def documents(root):
    for base in ("harness", ".agents/skills", ".claude/skills", ".claude/rules"):
        for current, dirs, files in os.walk(root / base):
            relative = Path(current).relative_to(root)
            dirs[:] = sorted(set(dirs) - SKIP)
            if relative in EXCLUDED:
                dirs[:] = [name for name in dirs if relative == Path("harness/project/testing/evidence")
                           and name in ("work", "harness")]
                files = [name for name in files if name == "README.human.md"]
            yield from (relative / name for name in sorted(files) if name.endswith(".md"))
    yield from map(Path, ("AGENTS.md", "CLAUDE.md",
                          "harness/common/base/AGENTS.template", "harness/common/base/CLAUDE.template"))


def owner(source):
    if source.parts[:2] in ((".agents", "skills"), (".claude", "skills"), (".claude", "rules")):
        return [Path("harness", p, *source.parts[1:]) for p in PACKAGES]
    if source.name in ("AGENTS.md", "CLAUDE.md") and len(source.parts) == 1:
        return [Path("harness/common/base", source.stem + ".template")]
    return []


def mirrored(source):
    return bool(owner(source) or (len(source.parts) >= 4 and source.parts[0] == "harness" and
                                 (source.parts[2] in ("rules", "skills") or
                                  source.suffix == ".template")))


def section(target, fragment):
    tokens = PARSER.parse(target.read_text())
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            name = tokens[index + 1].content
            if re.sub(r"[^\w -]", "", name.lower()).replace(" ", "-") == fragment:
                return
    raise ValueError(f"Unknown section {target}#{fragment}")


def inspect(root, source, writer, totals):
    document = root / source
    text = document.read_text()
    candidates = owner(source)
    if candidates:
        matches = [root / p for p in candidates if (root / p).is_file()]
        if len(matches) != 1 or document.read_bytes() != matches[0].read_bytes():
            raise ValueError(f"Missing, ambiguous or differing canonical source for {source}")
    totals["documents"] += 1
    for block in PARSER.parse(text):
        tokens = block.children or []
        for i, token in enumerate(tokens):
            if token.type == "code_inline" and mirrored(source) and ROOT_PATH.fullmatch(token.content):
                kind, href = "root", token.content
                target = root / href
            elif token.type in ("link_open", "image"):
                href = token.attrGet("href" if token.type == "link_open" else "src")
                if token.attrGet("title") is not None:
                    raise ValueError(f"Unnecessary title in {source}: {href}")
                url = urlsplit(href)
                if url.scheme or url.netloc:
                    writer.writerow([source, "external", href, href, "-"])
                    totals["external"] += 1
                    continue
                if mirrored(source) or not url.path or url.path.startswith("/"):
                    raise ValueError(f"Expected another path format in {source}: {href}")
                target = document.parent / unquote(url.path)
                kind = "markdown"
                label = token.content
                if token.type == "link_open":
                    pieces = []
                    for child in tokens[i + 1:]:
                        if child.type == "link_close":
                            break
                        pieces.append(child.content)
                    label = "".join(pieces)
                if label != target.name:
                    raise ValueError(f"Label does not match {target.name} in {source}")
                if url.fragment:
                    section(target, unquote(url.fragment))
            else:
                continue
            target = target.resolve(strict=True)
            relative = target.relative_to(root)
            digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else "directory"
            writer.writerow([source, kind, href, relative, digest])
            totals[kind] += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--request", type=Path, help="Current INBOX directory relative to repository root")
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    files = documents(root)
    if args.request:
        files = [args.request / name for name in ("README.human.md", "request.md", "plan.md", "specification.md")]
    totals = dict.fromkeys(("documents", "markdown", "root", "external"), 0)
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["source", "format", "reference", "resolved_target", "sha256_or_type"])
    for source in files:
        inspect(root, source, writer, totals)
    print(totals, file=sys.stderr)


if __name__ == "__main__":
    main()
