"""Publish one explicitly approved startup set. Python 3.9+, POSIX.

Run from the author installation. The request supplies publication.json, candidate/
with repository-relative canonical paths, publication-report.md, and a separate
publication-approval.json recording the user's decision. This utility does not
grant approval, create its receipt, or update the request's verification status.

Before passing --initial-cutover, the operator must quiesce previous sessions
and writers: the legacy startup checker does not know the journal or the lock.
After an interruption, reuse exactly the same request, digest and reference.
"""

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Optional
import re
import stat
import sys


try:
    import fcntl
except ImportError:
    fcntl = None

DIRECTORY = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
JOURNAL = ".harness-publication.json"
CHECKER = "harness/common/checks/ensure_entrypoint_links.py"
AUTHOR_LAYOUT = "harness/AGENTS.bootstrap.md.in"
TEMPLATES = {"harness/common/base/AGENTS.template": "AGENTS.md",
             "harness/common/base/CLAUDE.template": "CLAUDE.md"}
LEGACY = {"harness/common/START.md", "harness/project/START.md",
          "harness/common/base/AGENTS.bootstrap.json"}
COMMON_PROGRAMS = {CHECKER, "harness/common/checks/check_human_guide_search.py",
                   "harness/common/scripts/publish_startup_set.py", "harness/common/scripts/run_tests.py"}
# Existing documents included in the startup link migration. They have no installed mirrors.
MIGRATION_DOCUMENTS = {
    "harness/common/decisions/2026-10-04-user-owned-entrypoints.md",
    "harness/common/decisions/2026-10-05-harness-architecture.md",
    "harness/common/decisions/2026-10-05-inbox-execution-status.md",
    "harness/common/decisions/2026-10-05-skill-rule-ownership.md",
    "harness/common/decisions/2026-10-06-dependencies-through-uv.md",
    "harness/common/decisions/2026-10-06-harness-structure.md",
    "harness/common/decisions/2026-10-06-plugin-eval-human-filter.md",
    "harness/common/decisions/2026-10-07-skills-first-knowledge.md",
    "harness/common/decisions/2026-11-24-workflow-decision-recording.md",
    "harness/common/docs/2026-10-05-compact-authoring.md",
    "harness/common/docs/2026-10-05-protected-entrypoints.md",
    "harness/common/docs/2026-10-05-skill-rule-ownership-contract.md",
    "harness/common/docs/2026-10-06-plugin-eval-without-human.md",
    "harness/common/docs/2026-10-06-run-tests.md",
    "harness/common/specs/2026-10-06-structure-and-creation-dates.md",
}
DIGEST = re.compile(r"[a-f0-9]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def json_object(pairs):
    fields = dict(pairs)
    require(len(fields) == len(pairs), "duplicate JSON field")
    return fields


def fields(item, names):
    require(isinstance(item, dict) and set(item) == set(names.split()),
            f"expected fields: {names}")


def safe_path(value, native=False):
    require(isinstance(value, str) and value and all(
        part and (not part.startswith(".") or native and index == 0 and part in (".claude", ".agents"))
        and "\\" not in part
        and all(ch.isprintable() for ch in part) for index, part in enumerate(value.split("/"))
    ), f"invalid repository-relative path: {value!r}")
    return value


def digest(value, optional=False):
    require((optional and value is None) or
            (isinstance(value, str) and DIGEST.fullmatch(value)),
            "expected a lowercase SHA-256 (or null for an absent file)")
    return value


@contextmanager
def directory(start_fd, parts, create=False):
    """Walk from an open directory without following links."""
    fd = os.dup(start_fd)
    try:
        for part in parts:
            try:
                child = os.open(part, DIRECTORY, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, mode=0o755, dir_fd=fd)
                os.fsync(fd)
                child = os.open(part, DIRECTORY, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


@contextmanager
def locked_root(root):
    require(fcntl is not None and hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW")
            and os.open in os.supports_dir_fd and os.rename in os.supports_dir_fd,
            "publication requires POSIX flock and no-follow directory file descriptors")
    path = Path(root).absolute()
    require(".." not in path.parts, "root must not contain '..'")
    anchor = os.open(path.anchor, DIRECTORY)
    try:
        with directory(anchor, path.parts[1:]) as root_fd:
            fcntl.flock(root_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield root_fd
    finally:
        os.close(anchor)


def entry_kind(root, path):
    parts = path.split("/")
    try:
        with directory(root, parts[:-1]) as parent:
            mode = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False).st_mode
    except FileNotFoundError:
        return None
    if stat.S_ISDIR(mode):
        return "directory"
    require(stat.S_ISREG(mode), f"unexpected file type: {path}")
    return "file"


def children(root, path):
    if entry_kind(root, path) is None:
        return []
    with directory(root, path.split("/")) as parent:
        return sorted(os.listdir(parent))


def descendants(root, path):
    for name in children(root, path):
        child = path + "/" + name
        kind = entry_kind(root, child)
        yield child, kind
        if kind == "directory":
            yield from descendants(root, child)


def check_native_inventory(root, working, temporary_paths):
    """A future approved row may name a not-yet-existing source during resume."""
    allowed = {c.path for c in working} | set(temporary_paths)
    for path in list(allowed):
        parts = path.split("/")
        allowed.update("/".join(parts[:n]) for n in range(1, len(parts)))

    rules = ".claude/rules"
    for path, kind in descendants(root, rules):
        if kind != "file" or not path.lower().endswith(".md") or path in allowed:
            continue
        relative = path[len(rules) + 1:]
        name = relative.split("/")[-1]
        package = "common" if name.startswith("comm-") else "project"
        prefix = "comm-" if package == "common" else "proj-"
        require(name.startswith(prefix) and name.endswith(".md") and
                entry_kind(root, f"harness/{package}/rules/{relative}") == "file",
                f"unmanaged native rule: {path}")
    for folder in (".claude/skills", ".agents/skills"):
        for name in children(root, folder):
            if not name.startswith(("comm-", "proj-")):
                continue
            package = "common" if name.startswith("comm-") else "project"
            top = folder + "/" + name
            source = f"harness/{package}/skills/{name}"
            require(entry_kind(root, top) == "directory" and
                    (top in allowed or entry_kind(root, source) == "directory"),
                    f"unmanaged native skill: {top}")
            for path, kind in descendants(root, top):
                require(path in allowed or entry_kind(root, source + path[len(top):]) == kind,
                        f"unexpected native skill entry: {path}")


@dataclass(frozen=True)
class Metadata:
    inode: tuple
    times: tuple
    uid: int
    gid: int
    mode: int
    attributes: dict


def attributes(fd):
    if not hasattr(os, "listxattr"):
        return {}
    return {key: os.getxattr(fd, key) for key in os.listxattr(fd)}


def snapshot(stat_result, attrs):
    return Metadata((stat_result.st_dev, stat_result.st_ino),
                    (stat_result.st_mtime_ns, stat_result.st_ctime_ns, stat_result.st_size),
                    stat_result.st_uid, stat_result.st_gid, stat.S_IMODE(stat_result.st_mode), attrs)


def preserve(fd, metadata):
    current = os.fstat(fd)
    if (current.st_uid, current.st_gid) != (metadata.uid, metadata.gid):
        os.fchown(fd, metadata.uid, metadata.gid)
    if hasattr(os, "listxattr"):
        inherited = attributes(fd)
        for key in inherited.keys() - metadata.attributes.keys():
            os.removexattr(fd, key)
        for key, value in metadata.attributes.items():
            if inherited.get(key) != value:
                os.setxattr(fd, key, value)
    os.fchmod(fd, metadata.mode)
    actual = os.fstat(fd)
    require((actual.st_uid, actual.st_gid, stat.S_IMODE(actual.st_mode), attributes(fd)) ==
            (metadata.uid, metadata.gid, metadata.mode, metadata.attributes),
            "cannot preserve file ownership, mode or extended attributes")


def read_at(parent, name):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        fd = os.open(name, flags, dir_fd=parent)
    except FileNotFoundError:
        return None, None
    with os.fdopen(fd, "rb") as file:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), f"expected regular file: {name}")
        data = file.read()
        attrs = attributes(fd)
        metadata = snapshot(before, attrs)
        require(snapshot(os.fstat(fd), attrs) == metadata, f"file changed while reading: {name}")
        return data, metadata


def read(root, path):
    parts = path.split("/")
    try:
        with directory(root, parts[:-1]) as parent:
            return read_at(parent, parts[-1])[0]
    except FileNotFoundError:
        return None


def read_json(root, path):
    data = read(root, path)
    require(data is not None, f"required input missing: {path}")
    return json.loads(data.decode("utf-8"), object_pairs_hook=json_object), sha(data)


def temporary_path(path, after):
    identity = hashlib.sha256((path + ":" + after).encode()).hexdigest()
    folder, separator, _ = path.rpartition("/")
    return folder + separator + ".harness-publish-" + identity


def write_checked(root, path, before, data):
    """One durable replacement or unlink, with the expected old digest."""
    parts = path.split("/")
    name = parts[-1]
    with directory(root, parts[:-1], create=data is not None) as parent:
        old, metadata = read_at(parent, name)
        require(sha(old) == before, f"concurrent change: {path}")
        if data is None:
            require(read_at(parent, name) == (old, metadata), f"concurrent change: {path}")
            os.unlink(name, dir_fd=parent)
        else:
            temporary = temporary_path(path, sha(data)).split("/")[-1]
            fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644,
                         dir_fd=parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    if metadata is not None:
                        preserve(stream.fileno(), metadata)
                    os.fsync(stream.fileno())
                require(read_at(parent, name) == (old, metadata), f"concurrent change: {path}")
                os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
            finally:
                try:
                    os.unlink(temporary, dir_fd=parent)
                except FileNotFoundError:
                    pass
        os.fsync(parent)


def working_paths(path):
    """Validate canonical ownership; enumerate all mirrors of this file."""
    parts = path.split("/")
    require(len(parts) >= 3 and parts[0] == "harness" and
            parts[1] in ("common", "project"), f"outside canonical packages: {path}")
    package, category = parts[1:3]
    prefix = "comm-" if package == "common" else "proj-"
    if path in TEMPLATES:
        return [TEMPLATES[path]]
    if category == "rules" and len(parts) >= 4 and parts[-1].endswith(".md"):
        if parts[-1] == "README.human.md":
            return []
        require(parts[-1].startswith(prefix), f"rule owner mismatch: {path}")
        return [".claude/rules/" + "/".join(parts[3:])]
    if category == "skills" and len(parts) >= 5:
        require(parts[3].startswith(prefix), f"skill owner mismatch: {path}")
        suffix = "/".join(parts[3:])
        return [".agents/skills/" + suffix, ".claude/skills/" + suffix]
    if path in LEGACY | COMMON_PROGRAMS | MIGRATION_DOCUMENTS or parts[2:] == ["INDEX.md"]:
        return []
    if category == "testing" and len(parts) == 5:
        if parts[3:] == ["acceptance", "acceptance.md"]:
            return []
        if parts[3] == "tests" and (parts[4] == "conftest.py" or
                                    re.fullmatch(r"test_[A-Za-z0-9_]+\.py", parts[4])):
            return []
    raise ValueError(f"outside startup publication scope: {path}")


@dataclass(frozen=True)
class Change:
    path: str
    before: Optional[str]
    after: Optional[str]
    source: str = ""


def plan(manifest, request, initial):
    fields(manifest, "schema request canonical working retire report_sha256")
    require(type(manifest["schema"]) is int and manifest["schema"] == 1 and
            manifest["request"] == request, "manifest schema or request mismatch")
    for key in ("canonical", "working", "retire"):
        require(isinstance(manifest[key], list), f"expected array: {key}")
    digest(manifest["report_sha256"])
    canonical, working, retire = [], [], []
    mirrored = {}
    for row in manifest["canonical"]:
        fields(row, "path before after")
        path = safe_path(row["path"])
        before, after = digest(row["before"], True), digest(row["after"], True)
        require(before is not None or after is not None, f"empty operation: {path}")
        require(path not in LEGACY or (initial and after is None),
                f"legacy removal requires --initial-cutover: {path}")
        require(after is not None or path not in set(TEMPLATES) | COMMON_PROGRAMS,
                f"cannot remove a bootstrap component: {path}")
        for destination in working_paths(path):
            require(destination not in mirrored, f"duplicate working path: {destination}")
            mirrored[destination] = (path, after)
        canonical.append(Change(path, before, after, request + "/candidate/" + path))
    for row in manifest["working"]:
        fields(row, "path source before after")
        path, source = safe_path(row["path"], native=True), safe_path(row["source"])
        before, after = digest(row["before"], True), digest(row["after"], True)
        require(mirrored.get(path) == (source, after), f"unbound working copy: {path}")
        del mirrored[path]
        working.append(Change(path, before, after, source))
    require(not mirrored, "missing working mirrors: " + ", ".join(sorted(mirrored)))
    for row in manifest["retire"]:
        fields(row, "path before")
        require(initial and row["path"] == AUTHOR_LAYOUT,
                "only the legacy author layout can be retired with --initial-cutover")
        retire.append(Change(AUTHOR_LAYOUT, digest(row["before"]), None))
    paths = [change.path for change in canonical + working + retire]
    require(paths and len(set(paths)) == len(paths), "empty set or duplicate path")
    if initial:
        require(any(c.path == CHECKER and c.after for c in canonical),
                "first cutover must include the journal-aware checker")
    canonical.sort(key=lambda change: change.path != CHECKER)
    return canonical, working, retire


def skill_retirements(root, canonical, working):
    """An entire skill can retire only by deleting every file in all copies."""
    by_path = {c.path: c.after for c in canonical + working}
    result = {}
    for change in canonical:
        parts = change.path.split("/")
        if len(parts) < 5 or parts[2] != "skills":
            continue
        owner = "/".join(parts[:4])
        skill = owner + "/SKILL.md"
        if skill not in by_path:
            require(entry_kind(root, skill) == "file", f"incomplete canonical skill: {owner}")
        elif by_path[skill] is None:
            require(change.after is None, f"new content in retired skill: {owner}")
            result[owner] = [owner, ".claude/skills/" + parts[3], ".agents/skills/" + parts[3]]
    for copies in result.values():
        for folder in copies:
            for path, kind in descendants(root, folder):
                if kind == "file":
                    require(path in by_path and by_path[path] is None,
                            f"unapproved remaining file in retired skill: {path}")
    return result


def prune_empty(root, folder):
    """Remove only now-empty directories inside the specifically retired skill."""
    if entry_kind(root, folder) is None:
        return
    dirs = [path for path, kind in descendants(root, folder) if kind == "directory"]
    for path in reversed([folder] + dirs):
        parts = path.split("/")
        with directory(root, parts[:-1]) as parent:
            os.rmdir(parts[-1], dir_fd=parent)
            os.fsync(parent)


def publish(root, request, approved_hash, approval_id, initial=False):
    request = safe_path(request)
    require(re.fullmatch(r"harness/(common|project)/inbox/[^/]+", request),
            "expected a single request folder within a package inbox")
    require(isinstance(approval_id, str) and approval_id.strip(), "missing user decision reference")
    digest(approved_hash)
    manifest, manifest_hash = read_json(root, request + "/publication.json")
    require(manifest_hash == approved_hash, "manifest differs from approved SHA-256")
    approval, receipt_hash = read_json(root, request + "/publication-approval.json")
    require(approval == {"request": request, "decision": "publish",
                         "manifest_sha256": approved_hash, "reference": approval_id},
            "missing matching explicit publication decision")
    if any(entry_kind(root, p) is not None for p in LEGACY | {AUTHOR_LAYOUT}):
        require(initial, "legacy startup files present: quiesce old sessions and use --initial-cutover")
    canonical, working, retire = plan(manifest, request, initial)
    report = read(root, request + "/publication-report.md")
    require(report and sha(report) == manifest["report_sha256"],
            "verification report missing or changed")
    record = {"request": request, "manifest_sha256": approved_hash,
              "approval_sha256": receipt_hash, "initial_cutover": initial}
    marker = (json.dumps(record, sort_keys=True) + "\n").encode()
    previous = read(root, JOURNAL)
    require(previous is None or previous == marker, "another or changed publication journal")
    for change in canonical:
        if change.after is not None:
            require(sha(read(root, change.source)) == change.after,
                    f"approved candidate missing or changed: {change.path}")
    changes = canonical + working + retire
    # A kill between creating a temp and rename can leave an approved partial file.
    # On a fresh run every operation's deterministic scratch name must be free.
    # The journal's own pre-rename scratch can be left before the marker appears.
    candidate_by_path = {c.path: c.source for c in canonical}
    temporary_sources = {temporary_path(c.path, c.after): c.source
                         for c in canonical if c.after is not None}
    temporary_sources.update({temporary_path(c.path, c.after): candidate_by_path[c.source]
                              for c in working if c.after is not None})
    marker_temp = temporary_path(JOURNAL, sha(marker))
    stale = {}
    for path, source in list(temporary_sources.items()) + [(marker_temp, None)]:
        partial = read(root, path)
        if partial is not None:
            require(previous is not None or path == marker_temp, f"reserved path occupied: {path}")
            expected = marker if source is None else read(root, source)
            require(expected is not None and expected.startswith(partial),
                    f"unrecognized temporary content: {path}")
            stale[path] = sha(partial)
    check_native_inventory(root, working, stale)
    retire_skills = skill_retirements(root, canonical, working)
    states = {c.path: sha(read(root, c.path)) for c in changes}
    if all(states[c.path] == c.after for c in changes) and previous is None and not stale:
        return
    for c in changes:
        allowed = (c.before, c.after) if previous is not None else (c.before,)
        require(states[c.path] in allowed, f"unexpected version before publication: {c.path}")
    for path, expected_hash in stale.items():
        write_checked(root, path, expected_hash, None)
    if previous is None:
        write_checked(root, JOURNAL, None, marker)

    for stage in (canonical, working, retire):
        for c in stage:
            current = sha(read(root, c.path))
            require(current in (c.before, c.after), f"unexpected version: {c.path}")
            if current == c.after:
                continue
            data = None if c.after is None else read(root, c.source)
            require(sha(data) == c.after, f"source changed: {c.source}")
            write_checked(root, c.path, current, data)
        if stage is canonical or stage is working:
            for copies in retire_skills.values():
                for folder in (copies[:1] if stage is canonical else copies[1:]):
                    prune_empty(root, folder)
        for c in stage:
            require(sha(read(root, c.path)) == c.after, f"stage verification failed: {c.path}")
    for c in changes:
        require(sha(read(root, c.path)) == c.after, f"final verification failed: {c.path}")
    if previous is not None:
        # A killed writer may already have renamed an entry but not synced its
        # containing directory. Make observed after-states durable before unlock.
        parents = {tuple(c.path.split("/")[:-1]) for c in changes}
        for parts in parents:
            while parts and entry_kind(root, "/".join(parts)) is None:
                parts = parts[:-1]
            with directory(root, parts) as parent:
                os.fsync(parent)
    write_checked(root, JOURNAL, sha(marker), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--request", required=True)
    parser.add_argument("--approve-sha256", required=True)
    parser.add_argument("--approval-id", required=True)
    parser.add_argument("--initial-cutover", action="store_true",
                        help="operator confirms old sessions and writers are quiescent")
    args = parser.parse_args()
    try:
        with locked_root(args.root) as root:
            publish(root, args.request, args.approve_sha256, args.approval_id,
                    args.initial_cutover)
    except (OSError, ValueError) as error:
        print(f"Publication stopped: {error}", file=sys.stderr)
        return 2
    print("Approved file set verified. Check fresh startup before updating the request status.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
